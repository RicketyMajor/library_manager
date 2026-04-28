from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import GuildProfile, Adventurer, DeepWorkSession, AdventurerClass, AdventurerRace, AdventurerGender, DailyHabit, DailyStatistic, HabitDifficulty, InventorySlot, ItemRarity
import random
from .engine import process_session_completion, generate_session_script, consolidate_wealth, distribute_random_stats, evaluate_daily_penalties, universal_consolidate
from django.utils import timezone
from datetime import timedelta


def fmt_item_rich(item, default="Vacío"):
    """Devuelve el nombre del item envuelto en su color de rareza para la TUI."""
    if not item:
        return default
    color = ItemRarity.get_color(item.rarity)
    return f"[{color}]{item.name}[/]"


@api_view(['GET'])
def guild_status(request):
    """Devuelve el estado general del Gremio y la lista de aventureros con sus stats de RPG."""
    guild, _ = GuildProfile.objects.get_or_create(id=1)
    adventurers = Adventurer.objects.all()

    adv_data = []
    for adv in adventurers:
        mods = adv.get_stat_modifiers()

        def fmt_stat(base, stat_key):
            """Genera el texto enriquecido para la TUI (Ej: 15 [+2])"""
            mod = mods.get(stat_key, 0)
            total = base + mod
            if mod > 0:
                return f"{total} [bold green](+{mod})[/bold green]"
            elif mod < 0:
                return f"{total} [bold red]({mod})[/bold red]"
            return str(total)

        adv_data.append({
            "id": adv.id,
            "name": adv.name,
            "class_name": adv.get_adv_class_display(),
            "race": adv.get_race_display(),
            "level": adv.level,
            "xp": adv.experience,
            "hp": f"{adv.current_hp}/{adv.max_hp}",

            # --- Estadísticas Formateadas con Color ---
            "str": fmt_stat(adv.base_str, 'str'),
            "dex": fmt_stat(adv.base_dex, 'dex'),
            "con": fmt_stat(adv.base_con, 'con'),
            "int": fmt_stat(adv.base_int, 'int'),
            "wis": fmt_stat(adv.base_wis, 'wis'),
            "cha": fmt_stat(adv.base_cha, 'cha'),
            "luk": fmt_stat(adv.base_luk, 'luk'),

            # --- Combate Real ---
            "combat_armor": mods['armor'],
            "combat_damage": f"{mods['weapon_dice_count']}d{mods['weapon_dice_sides']} + {mods['damage']}",

            "wealth": {
                "iron_half_penny": adv.iron_half_penny, "iron_penny": adv.iron_penny,
                "ardite": adv.ardite, "drabin": adv.drabin, "copper_penny": adv.copper_penny,
                "iota": adv.iota, "silver_penny": adv.silver_penny, "sueldo": adv.sueldo,
                "talento": adv.talento, "real": adv.real, "marco": adv.marco
            },
            "wealth_summary": f"{adv.talento}T, {adv.iota}i, {adv.ardite}a",
            # --- SLOTS ---
            "equip_main_hand": fmt_item_rich(adv.equip_main_hand, "Desarmado"),
            "equip_off_hand": fmt_item_rich(adv.equip_off_hand),
            "equip_head": fmt_item_rich(adv.equip_head),
            "equip_torso": fmt_item_rich(adv.equip_torso, "Ropa común"),
            "equip_hands": fmt_item_rich(adv.equip_hands),
            "equip_legs": fmt_item_rich(adv.equip_legs),
            "equip_feet": fmt_item_rich(adv.equip_feet),
            "equip_necklace": fmt_item_rich(adv.equip_necklace, "Ninguno"),
            "equip_ring_1": fmt_item_rich(adv.equip_ring_1),
            "equip_ring_2": fmt_item_rich(adv.equip_ring_2),
            "equip_bracelet": fmt_item_rich(adv.equip_bracelet, "Ninguno"),
            "equip_earring": fmt_item_rich(adv.equip_earring, "Ninguno"),

            "fatigue": adv.fatigue_stacks
        })

    guild_data = {
        "level": guild.level,
        "xp": guild.experience,
        "net_worth_talents": guild.net_worth_in_talents,
        "inventory": {
            "iron_half_penny": guild.iron_half_penny,
            "iron_penny": guild.iron_penny,
            "ardite": guild.ardite,
            "drabin": guild.drabin,
            "copper_penny": guild.copper_penny,
            "iota": guild.iota,
            "silver_penny": guild.silver_penny,
            "sueldo": guild.sueldo,
            "talento": guild.talento,
            "real": guild.real,
            "marco": guild.marco
        }
    }

    return Response({
        "guild": guild_data,
        "adventurers": adv_data
    })


@api_view(['POST'])
def consolidate_guild_wealth(request):
    """Llama al motor para consolidar la riqueza del gremio (Mesa del Cambista)."""
    # El ID 1 siempre representa a tu Gremio principal
    result = consolidate_wealth(1)
    if result.get("status") == "error":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response(result)


@api_view(['POST'])
def start_session(request):
    """Crea la sesión al inicio y devuelve el guion de eventos pre-calculado."""
    data = request.data
    duration = data.get('duration_minutes', 25)
    category = data.get('category', 'General')
    adventurer_ids = data.get('adventurer_ids', [])

    # Crea la sesión en el momento para obtener un ID único que sirva de semilla
    session = DeepWorkSession.objects.create(
        duration_minutes=duration,
        category=category,
        completed=False
    )

    if adventurer_ids:
        adventurers = Adventurer.objects.filter(id__in=adventurer_ids)
        session.adventurers_involved.set(adventurers)
        session.save()
    else:
        adventurers = []

    # el Oráculo genera el destino
    script = generate_session_script(session.id, duration, adventurers)

    return Response({
        "status": "success",
        "session_id": session.id,
        "script": script
    })


@api_view(['POST'])
def complete_session(request):
    """Cierra la sesión aplicando el botín ganado según el tiempo sobrevivido."""
    data = request.data
    session_id = data.get('session_id')
    survived_seconds = data.get('survived_seconds')

    if not session_id:
        return Response({"status": "error", "message": "Falta el ID de la sesión."}, status=status.HTTP_400_BAD_REQUEST)

    # El motor procesa la realidad basándose en cuánto tiempo se aguantate sin distracciones, y devuelve el resultado de la expedición
    result = process_session_completion(session_id, survived_seconds)

    if result.get("status") == "error":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "status": "success",
        "message": "Expedición finalizada.",
        "log": result.get("log", []),
        "engine_details": result
    })


@api_view(['POST'])
def create_adventurer(request):
    """Crea un aventurero. Verifica el límite de cupos del Gremio."""
    guild, _ = GuildProfile.objects.get_or_create(id=1)

    # 1 cupo por cada Nivel del Gremio
    if Adventurer.objects.count() >= guild.level:
        return Response({
            "status": "error",
            "message": f"Gremio Nv. {guild.level} lleno. Estudia y sube de nivel para tener más cupos."
        }, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    stats = data.get('stats', None)

    adv = Adventurer.objects.create(
        name=data.get('name', 'Aventurero Desconocido'),
        adv_class=data.get('adv_class', 'FTR'),
        race=data.get('race', 'HUM'),
        gender=data.get('gender', 'O'),
        max_hp=25,
        current_hp=25,
        # Si vienen stats de la taberna, los asignamos. Si no, 0.
        base_str=stats['str'] if stats else 0, base_dex=stats['dex'] if stats else 0,
        base_con=stats['con'] if stats else 0, base_int=stats['int'] if stats else 0,
        base_wis=stats['wis'] if stats else 0, base_cha=stats['cha'] if stats else 0,
        base_luk=stats['luk'] if stats else 0
    )

    # Si es el primer avatar manual, reparte al azar los 13 pts.
    if not stats:
        distribute_random_stats(adv, 13)

    return Response({"status": "success", "message": f"{adv.name} ha firmado el contrato."})


@api_view(['GET'])
def tavern_recruits(request):
    """Genera 3 reclutas procedurales con nombres y stats aleatorios."""
    prefixes = ["Thor", "Grim", "Ar", "Leg", "Kvoth", "El",
                "Fae", "Gael", "Bae", "Mor", "Dae", "Val", "Gim"]
    suffixes = ["din", "gar", "agorn", "olas", "e", "rond",
                "lin", "dor", "th", "gan", "mon", "ria", "li"]

    recruits = []
    for _ in range(3):
        # Generación de Identidad
        name = random.choice(prefixes) + random.choice(suffixes)
        adv_class_obj = random.choice(AdventurerClass.choices)
        race_obj = random.choice(AdventurerRace.choices)
        gender_obj = random.choice(AdventurerGender.choices)

        # Reparto Procedural de los 13 Puntos Base
        stats = {'str': 0, 'dex': 0, 'con': 0,
                 'int': 0, 'wis': 0, 'cha': 0, 'luk': 0}
        keys = list(stats.keys())
        for _ in range(13):
            stats[random.choice(keys)] += 1

        recruits.append({
            "name": name,
            "adv_class": adv_class_obj[0],
            "adv_class_display": adv_class_obj[1],
            "race": race_obj[0],
            "race_display": race_obj[1],
            "gender": gender_obj[0],
            "stats": stats
        })
    return Response({"recruits": recruits})


@api_view(['DELETE'])
def delete_adventurer(request, adv_id):
    """Elimina un aventurero de la base de datos."""
    try:
        adv = Adventurer.objects.get(id=adv_id)
        name = adv.name
        adv.delete()
        return Response({"status": "success", "message": f"{name} ha sido eliminado del Gremio."})
    except Adventurer.DoesNotExist:
        return Response({"status": "error", "message": "Aventurero no encontrado."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_habits(request):
    """Lista todos los hábitos y evalúa penalizaciones de días anteriores."""
    # Al consultar el tablón, el motor revisa si hay deudas de días pasados
    penalties = evaluate_daily_penalties()

    today = timezone.now().date()
    habits = DailyHabit.objects.all()

    habit_list = []
    for h in habits:
        habit_list.append({
            "id": h.id,
            "name": h.name,
            "difficulty": h.get_difficulty_display(),
            "completed_today": h.last_completed_date == today
        })

    return Response({
        "habits": habit_list,
        "penalties_applied": penalties
    })


@api_view(['POST'])
def create_habit(request):
    """Crea un nuevo hábito desde la TUI."""
    data = request.data
    habit = DailyHabit.objects.create(
        name=data.get('name'),
        difficulty=data.get('difficulty', 'C')
    )
    return Response({"status": "success", "message": f"Hábito '{habit.name}' añadido al tablón."})


@api_view(['POST'])
def complete_habit(request):
    """Marca un hábito como hecho, otorga recompensas y cura fatiga."""
    today = timezone.now().date()
    habit_id = request.data.get('habit_id')

    try:
        habit = DailyHabit.objects.get(id=habit_id)
        if habit.last_completed_date == today:
            return Response({"status": "warning", "message": "Ya cumpliste este hábito hoy."})

        guild, _ = GuildProfile.objects.get_or_create(id=1)
        adventurers = Adventurer.objects.all()

        # --- DEFINICIÓN DE RECOMPENSAS POR RANGO ---
        rewards = {
            'S': {'xp': 100, 'coin': 'iota', 'amt': 1},
            'A': {'xp': 50,  'coin': 'copper_penny', 'amt': 5},
            'B': {'xp': 25,  'coin': 'copper_penny', 'amt': 2},
            'C': {'xp': 10,  'coin': 'ardite', 'amt': 5},
        }
        r = rewards.get(habit.difficulty)

        # Otorga XP al Gremio y verifica si sube de nivel
        old_level = guild.level
        guild.experience += r['xp']
        setattr(guild, r['coin'], getattr(guild, r['coin']) + r['amt'])

        while guild.experience >= 500:
            guild.level += 1
            guild.experience -= 500

        guild.save()

        lvl_msg = f" ¡Gremio Nv. {guild.level}!" if guild.level > old_level else ""

        for adv in adventurers:
            adv.experience += r['xp']
            # CADA HÁBITO CURA 1 PILA DE FATIGA
            if adv.fatigue_stacks > 0:
                adv.fatigue_stacks -= 1
            adv.save()

        habit.last_completed_date = today
        habit.save()

        return Response({
            "status": "success",
            "message": f"¡Hábito '{habit.name}' completado! +{r['xp']} XP y {r['amt']} {r['coin']}. Fatiga reducida.{lvl_msg}"
        })
    except DailyHabit.DoesNotExist:
        return Response({"status": "error", "message": "Hábito no encontrado."}, status=404)


@api_view(['GET'])
def get_stats_data(request):
    """Extrae los últimos 30 días de actividad para el gráfico."""
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    stats = DailyStatistic.objects.filter(
        date__gte=thirty_days_ago).order_order_by('date')

    data = {
        "dates": [s.date.strftime("%d/%m") for s in stats],
        "deep_work": [s.deep_work_minutes for s in stats],
        "screen_time": [s.screen_time_minutes for s in stats]
    }
    return Response(data)


@api_view(['GET'])
def get_inventory(request, target_type, target_id):
    """Obtiene el contenido de una mochila (aventurero) o del cofre (gremio)."""
    if target_type == 'guild':
        slots = InventorySlot.objects.filter(
            guild_id=target_id, quantity__gt=0)
    else:
        slots = InventorySlot.objects.filter(
            adventurer_id=target_id, quantity__gt=0)

    data = []
    for s in slots:
        data.append({
            "slot_id": s.id,
            "item_name": s.item.name,
            "color": ItemRarity.get_color(s.item.rarity),
            "type": s.item.get_item_type_display(),
            "qty": s.quantity,
            "stats": f"DMG:{s.item.bonus_damage} | ARM:{s.item.bonus_armor}"
        })
    return Response({"slots": data})


@api_view(['POST'])
def inventory_action(request):
    """Mueve objetos entre el Cofre y los Aventureros, o los vende."""
    action = request.data.get('action')
    slot_id = request.data.get('slot_id')
    adv_id = request.data.get('adv_id')

    try:
        slot = InventorySlot.objects.get(id=slot_id)
        guild = GuildProfile.objects.get(id=1)

        if action == "to_guild":
            if not slot.adventurer:
                return Response({"error": "Ya está en el cofre"}, status=400)
            g_slot, _ = InventorySlot.objects.get_or_create(
                guild=guild, item=slot.item, adventurer=None, defaults={'quantity': 0})
            g_slot.quantity += 1
            g_slot.save()

        elif action == "to_adv":
            if not slot.guild:
                return Response({"error": "No está en el cofre"}, status=400)
            target_adv = Adventurer.objects.get(id=adv_id)
            a_slot, _ = InventorySlot.objects.get_or_create(
                adventurer=target_adv, item=slot.item, guild=None, defaults={'quantity': 0})
            a_slot.quantity += 1
            a_slot.save()

        elif action == "sell":
            # Extrae el valor del objeto y lo inyecta al Gremio
            item = slot.item
            guild.iron_half_penny += item.cost_iron_half_penny
            guild.iron_penny += item.cost_iron_penny
            guild.ardite += item.cost_ardite
            guild.drabin += item.cost_drabin
            guild.copper_penny += item.cost_copper_penny
            guild.iota += item.cost_iota
            guild.silver_penny += item.cost_silver_penny
            guild.sueldo += item.cost_sueldo
            guild.talento += item.cost_talento
            guild.real += item.cost_real
            guild.marco += item.cost_marco
            guild.save()
            universal_consolidate(guild)  # Ordena el dinero automáticamente

        # Restar 1 al slot original (o borrarlo si queda vacío)
        slot.quantity -= 1
        if slot.quantity <= 0:
            slot.delete()
        else:
            slot.save()

        return Response({"status": "success", "message": "Acción completada con éxito."})

    except Exception as e:
        return Response({"error": str(e)}, status=400)
