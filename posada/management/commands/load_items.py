from django.core.management.base import BaseCommand
from posada.models import Item, ItemType, ItemRarity


class Command(BaseCommand):
    help = 'Puebla la base de datos con el catálogo completo de Armas, Armaduras y Objetos.'

    def handle(self, *args, **kwargs):
        # ==========================================
        # 📜 EL GRAN CATÁLOGO DE LA POSADA
        # Aquí puedes pegar todos los ítems de tu Excel.
        # ==========================================
        CATALOGO = [
            # --- TEMPLATE BASE PARA COPIAR Y PEGAR ---
            # {
            #     "name": "Nombre del Item",
            #     "description": "Descripción narrativa (opcional)",
            #     "item_type": "W1H|W2H|OFF|HED|TRS|LGS|HND|FET|NCK|RNG|BRC|EAR|CNS|MSC",
            #     "rarity": "COM|UNC|RAR|EPC|LEG",
            #     # --- ECONOMÍA (Borra las monedas que no uses o déjalas en 0) ---
            #     "cost_iron_half_penny": 0, "cost_iron_penny": 0, "cost_ardite": 0,
            #     "cost_drabin": 0, "cost_copper_penny": 0, "cost_iota": 0,
            #     "cost_silver_penny": 0, "cost_sueldo": 0, "cost_talento": 0,
            #     "cost_real": 0, "cost_marco": 0,
            #     # --- COMBATE ---
            #     "bonus_damage": 0, "bonus_armor": 0,
            #     # --- ESTADÍSTICAS RPG ---
            #     "bonus_str": 0, "bonus_dex": 0, "bonus_con": 0, "bonus_int": 0,
            #     "bonus_wis": 0, "bonus_cha": 0, "bonus_luk": 0,
            # },

            # ⚔️ EJEMPLO 1: Arma de Dos Manos (Poco Común)
            {
                "name": "Mandoble del Norte",
                "description": "Una espada pesada que requiere ambas manos. Destroza escudos.",
                "item_type": "W2H",
                "rarity": "UNC",
                "allowed_classes": ["WIZ", "SOR", "DRD"],
                "cost_silver_penny": 2,
                "cost_copper_penny": 5,  # Cuesta 2 platas y 5 cobres
                "bonus_damage": 8,
                "bonus_str": 3,
                "bonus_dex": -1,  # Las armas pesadas restan agilidad
            },

            # 🛡️ EJEMPLO 2: Armadura de Torso (Épica)
            {
                "name": "Cota de Escamas de Dragón",
                "description": "Forjada con escamas ardientes. Casi impenetrable.",
                "item_type": "TRS",
                "rarity": "EPC",
                "allowed_classes": ["WIZ", "SOR", "DRD"],
                "cost_talento": 1,
                "cost_iota": 5,  # Muy cara: 1 Talento y 5 Iotas
                "bonus_armor": 12,
                "bonus_con": 4,
                "bonus_cha": 2,  # Da prestigio llevarla
            },

            # 💍 EJEMPLO 3: Accesorio - Anillo (Legendario)
            {
                "name": "Anillo del Erudito Omnisciente",
                "description": "Otorga una claridad mental absoluta para el Deep Work.",
                "item_type": "RNG",
                "rarity": "LEG",
                "allowed_classes": ["WIZ", "SOR", "DRD"],
                "cost_marco": 2,  # Costo altísimo: 2 Marcos de Oro
                "bonus_int": 6,
                "bonus_wis": 5,
                "bonus_luk": 2,
            },

            # 🏺 EJEMPLO 4: Objeto Misceláneo (Raro)
            {
                "name": "Cáliz de Cristal Antiguo",
                "description": "No sirve para pelear, pero los coleccionistas pagan muy bien por él.",
                "item_type": "MSC",
                "rarity": "RAR",
                "allowed_classes": [],
                "cost_sueldo": 15,  # Objeto de lujo
                # Los objetos misceláneos generalmente no dan atributos de combate
            },
        ]

        self.stdout.write("Forjando los ítems en la base de datos...")
        items_creados = 0

        for data in CATALOGO:
            # Usamos update_or_create para que, si corres el script de nuevo,
            # se actualicen los precios en lugar de duplicar los ítems.
            item, created = Item.objects.update_or_create(
                name=data["name"],
                defaults={k: v for k, v in data.items() if k != "name"}
            )
            if created:
                items_creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'¡Éxito! Se forjaron {items_creados} ítems nuevos.'))
