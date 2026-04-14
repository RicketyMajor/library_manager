import random
from .models import GuildProfile, Adventurer, DeepWorkSession, GuildProfile

XP_PER_MINUTE = 10
# Bono si la clase del aventurero hace sinergia con la tarea
XP_MULTIPLIER_CLASS_MATCH = 1.5


def generate_session_script(session_id, duration_minutes, adventurers_qs):
    """
    El Oráculo: Genera el guion determinista de la sesión.
    Al usar el ID de la sesión como semilla, siempre generará la misma
    línea de tiempo de eventos para una misma expedición.
    """
    random.seed(session_id)

    script = []
    total_seconds = duration_minutes * 60
    adventurers = list(adventurers_qs)

    if not adventurers:
        random.seed()  # Restaurar semilla
        return script

    # Eventos de Botín menor - 1 a 3 ardites por minuto
    for m in range(duration_minutes):
        sec = (m * 60) + random.randint(5, 55)
        adv = random.choice(adventurers)
        amount = random.randint(1, 3)
        script.append({
            "second": sec, "type": "loot", "coin": "ardite", "amount": amount,
            "message": f"{adv.name} ha encontrado {amount} ardite(s) en la oscuridad."
        })

    # Eventos de Botín
    if duration_minutes >= 25:
        blocks = duration_minutes // 25
        for i in range(blocks):
            if random.random() < 0.60:
                sec = random.randint(i * 1500, (i+1) * 1500 - 1)
                adv = random.choice(adventurers)
                script.append({
                    "second": sec, "type": "loot", "coin": "iota", "amount": 1,
                    "message": f"¡Billo! {adv.name} ha desenterrado 1 Iota."
                })

    if duration_minutes >= 50:
        blocks = duration_minutes // 50
        for i in range(blocks):
            sec = random.randint(i * 3000, (i+1) * 3000 - 1)
            adv = random.choice(adventurers)
            if random.random() < 0.30:
                script.append({"second": sec, "type": "loot", "coin": "sueldo", "amount": 1,
                              "message": f"{adv.name} encontró 1 Sueldo de plata en un cofre oxidado."})
            elif random.random() < 0.05:
                script.append({"second": sec, "type": "loot", "coin": "talento", "amount": 1,
                              "message": f"¡UN TALENTO! {adv.name} apenas puede creer su suerte al ver el oro."})

    # Emboscadas
    ambush_blocks = duration_minutes // 20
    for i in range(ambush_blocks):
        if random.random() < 0.25:  # 25% de probabilidad de emboscada
            sec = random.randint(i * 1200, (i+1) * 1200 - 1)
            adv = random.choice(adventurers)
            script.append({
                "second": sec, "type": "injury", "adventurer_id": adv.id,
                "message": f"¡EMBOSCADA! {adv.name} ha resultado gravemente herido y necesitará recuperación."
            })

    # Eventos de Ambientación
    flavor_texts = [
        "{} afila su arma silenciosamente.",
        "{} revisa el mapa de la mazmorra con una antorcha.",
        "Se escucha un aullido a lo lejos. {} se pone en guardia.",
        "El silencio inunda la sala mientras {} lidera la marcha."
    ]
    flavor_count = duration_minutes // 10
    for _ in range(flavor_count):
        sec = random.randint(10, total_seconds - 10)
        adv = random.choice(adventurers)
        msg = random.choice(flavor_texts).format(adv.name)
        script.append(
            {"second": sec, "type": "flavor", "message": f"{msg}"})

    # Ordenar cronológicamente y restaurar la aletoriedad global
    script.sort(key=lambda x: x["second"])
    random.seed()
    return script


def distribute_tithe(guild, adventurers_qs, loot_dict, event_log):
    """
    Divide el botín: 70% al Cofre del Gremio, 30% dividido entre los aventureros.
    """
    num_adventurers = adventurers_qs.count()
    if num_adventurers == 0:
        for coin, amount in loot_dict.items():
            setattr(guild, coin, getattr(guild, coin) + amount)
        event_log.append("El Gremio ha reclamado el 100% del botín.")
        return

    event_log.append(
        f"El Gremio retiene el 70% del botín. El 30% se divide entre {num_adventurers} aventureros.")

    for coin, amount in loot_dict.items():
        if amount == 0:
            continue

        guild_share = int(amount * 0.70)
        adventurer_pool = amount - guild_share

        # El gremio guarda su parte
        setattr(guild, coin, getattr(guild, coin) + guild_share)

        # Repartir el sobrante a los aventureros
        if adventurer_pool > 0:
            share_per_adv = adventurer_pool // num_adventurers
            remainder = adventurer_pool % num_adventurers

            for index, adv in enumerate(adventurers_qs):
                # El resto se lo lleva el primer aventurero
                extra = remainder if index == 0 else 0
                setattr(adv, coin, getattr(adv, coin) + share_per_adv + extra)
                adv.save()

            # El Gremio se queda con el pico si nadie puede dividirlo bien
            if share_per_adv == 0 and remainder > 0:
                setattr(guild, coin, getattr(guild, coin) + remainder)


def market_phase(adventurers_qs, event_log):
    """
    Simula las decisiones de los aventureros en sus ratos libres.
    Revisan sus bolsillos y compran mejoras pasivas si tienen suficiente dinero.
    """
    for adv in adventurers_qs:
        # Tendencias de compra basadas en la clase
        is_martial = adv.adv_class in ['FTR', 'BBN', 'PAL', 'RGR']
        is_magic = adv.adv_class in ['WIZ', 'SOR', 'WLK', 'CLR', 'DRD']

        # ¿Tiene plata para comprar algo legendario?
        if adv.talento >= 1 or adv.sueldo >= 5:
            if is_martial:
                item = "Espada Larga Rúnica"
            else:
                item = "Tomo de Sabiduría Ancestral"

            # Paga el precio
            if adv.sueldo >= 5:
                adv.sueldo -= 5
            else:
                adv.talento -= 1

            event_log.append(
                f"Mercado: {adv.name} gastó plata en una reliquia: [{item}].")

        # ¿Tiene cobre para equipo decente?
        elif adv.iota >= 2 or adv.copper_penny >= 5:
            item = "Armadura de Malla" if is_martial else "Báculo de Roble"

            if adv.copper_penny >= 5:
                adv.copper_penny -= 5
            else:
                adv.iota -= 1

            event_log.append(
                f"Mercado: {adv.name} fue al herrero y compró: [{item}].")

        # Gasto de calderilla de hierro en consumibles o taberna
        elif adv.ardite >= 5:
            adv.ardite -= 5
            event_log.append(
                f"Mercado: {adv.name} gastó 5 ardites en raciones de viaje y pociones menores.")

        adv.save()


def process_session_completion(session_id, survived_seconds=None):
    try:
        session = DeepWorkSession.objects.get(id=session_id)
    except DeepWorkSession.DoesNotExist:
        return {"status": "error", "message": "Sesión no encontrada"}

    if session.completed:
        return {"status": "warning", "message": "Esta sesión ya fue procesada"}

    guild, _ = GuildProfile.objects.get_or_create(id=1)
    adventurers = session.adventurers_involved.all()
    event_log = []

    if survived_seconds is None:
        survived_seconds = session.duration_minutes * 60

    # Re-genera el guion exacto usando determinista
    script = generate_session_script(
        session.id, session.duration_minutes, adventurers)

    loot = {
        'iron_half_penny': 0, 'iron_penny': 0, 'ardite': 0, 'drabin': 0,
        'copper_penny': 0, 'iota': 0,
        'silver_penny': 0, 'sueldo': 0, 'talento': 0,
        'real': 0, 'marco': 0
    }

    # Procesar eventos ocurridos dentro del tiempo sobrevivido
    injured_ids = set()
    for event in script:
        if event["second"] <= survived_seconds:
            if event["type"] == "loot":
                loot[event["coin"]] += event["amount"]
            elif event["type"] == "injury":
                injured_ids.add(event["adventurer_id"])

    # Aplicar heridas
    for adv in adventurers:
        if adv.id in injured_ids:
            adv.is_recovering = True
            adv.recovery_time_left = 120  # 2 horas de cooldown
            adv.save()
            event_log.append(
                f"{adv.name} fue enviado a la enfermería en camilla.")

    # El Diezmo
    distribute_tithe(guild, adventurers, loot, event_log)

    # Fase de Mercado Autónomo
    market_phase(adventurers, event_log)

    # Experiencia (XP) - basada en minutos sobrevividos reales
    survived_minutes = survived_seconds // 60
    if survived_minutes < 1:
        survived_minutes = 1  # Bono de compasión

    base_xp = survived_minutes * XP_PER_MINUTE
    guild.experience += base_xp
    event_log.append(
        f"El Gremio gana {base_xp} XP por sobrevivir {survived_minutes} min.")

    for adv in adventurers:
        adv.experience += base_xp
        adv.save()

    guild.save()
    session.event_log = event_log
    session.completed = True
    session.save()

    return {
        "status": "success",
        "message": "Sesión completada y simulada.",
        "loot": loot,
        "base_xp": base_xp,
        "log": event_log
    }


def consolidate_wealth(guild_id):
    """
    Ejecuta las conversiones de la Mancomunidad de El Nombre del Viento.
    Procesa las monedas de menor valor y las empaqueta en divisas mayores.
    """
    try:
        guild = GuildProfile.objects.get(id=guild_id)
    except GuildProfile.DoesNotExist:
        return {"status": "error", "message": "Gremio no encontrado"}

    event_log = []

    # 11 Ardites = 1 Drabín
    if guild.ardite >= 11:
        new_drabines = guild.ardite // 11
        guild.ardite = guild.ardite % 11
        guild.drabin += new_drabines
        event_log.append(f"Se fundieron ardites en {new_drabines} Drabín(es).")

    # 10 Drabines = 1 Iota
    if guild.drabin >= 10:
        new_iotas = guild.drabin // 10
        guild.drabin = guild.drabin % 10
        guild.iota += new_iotas
        event_log.append(
            f"Se intercambiaron drabines por {new_iotas} Iota(s).")

    # 10 Iotas = 1 Talento
    if guild.iota >= 10:
        new_talentos = guild.iota // 10
        guild.iota = guild.iota % 10
        guild.talento += new_talentos
        event_log.append(
            f"Se consolidaron iotas en {new_talentos} Talento(s).")

    # 2 Medios peniques = 1 Penique de hierro
    if guild.iron_half_penny >= 2:
        new_iron = guild.iron_half_penny // 2
        guild.iron_half_penny = guild.iron_half_penny % 2
        guild.iron_penny += new_iron

    # 5 Peniques de hierro = 1 Penique de cobre
    if guild.iron_penny >= 5:
        new_copper = guild.iron_penny // 5
        guild.iron_penny = guild.iron_penny % 5
        guild.copper_penny += new_copper

    # 10 Peniques de cobre = 1 Penique de plata
    if guild.copper_penny >= 10:
        new_silver = guild.copper_penny // 10
        guild.copper_penny = guild.copper_penny % 10
        guild.silver_penny += new_silver

    # 32 Sueldos = 1 Talento
    if guild.sueldo >= 32:
        new_talentos_from_sueldo = guild.sueldo // 32
        guild.sueldo = guild.sueldo % 32
        guild.talento += new_talentos_from_sueldo
        event_log.append(
            f"Los sueldos se han convertido en {new_talentos_from_sueldo} Talento(s).")

    # 10 Talentos = 1 Marco
    if guild.talento >= 10:
        new_marcos = guild.talento // 10
        guild.talento = guild.talento % 10
        guild.marco += new_marcos
        event_log.append(f"¡Has acuñado {new_marcos} Marco(s) de Oro!")

    guild.save()

    return {
        "status": "success",
        "message": "Economía consolidada",
        "log": event_log
    }
