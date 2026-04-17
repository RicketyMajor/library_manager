from django.core.management.base import BaseCommand
from posada.models import Item, ItemType, ItemRarity


class Command(BaseCommand):
    help = 'Puebla la base de datos con el catálogo completo de Armas, Armaduras y Objetos.'

    def handle(self, *args, **kwargs):
        CATALOGO = [
            # --- TEMPLATE BASE PARA COPIAR Y PEGAR ---
            # {
            #     "name": "Nombre del Item",
            #     "description": "Descripción narrativa (opcional)",
            #     "item_type": "W1H|W2H|OFF|HED|TRS|LGS|HND|FET|NCK|RNG|BRC|EAR|CNS|MSC",
            #     "rarity": "COM|UNC|RAR|EPC|LEG",
            #     "allowed_classes": ["WIZ", "SOR", "DRD"],  # Lista de clases que pueden usarlo, dejar vacío si no hay restricciones
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

            # CONJUNTO DE ARMADURA DE TELA (Común)
            {
                "name": "Capucha de Tela",
                "description": "Una capucha hecha de tela cómoda. Proporciona cobertura ligera para la cabeza.",
                "item_type": "HED",
                "rarity": "COM",
                "allowed_classes": ["WIZ", "SOR", "DRD", "WLK"],
                "cost_ardite": 2,
                "cost_iron_penny": 5,
                "bonus_armor": 1,
            },

            {
                "name": "Túnica de Tela",
                "description": "Una túnica hecha de tela cómoda. Proporciona cobertura ligera para el cuerpo.",
                "item_type": "TRS",
                "rarity": "COM",
                "allowed_classes": ["WIZ", "SOR", "DRD", "WLK"],
                "cost_ardite": 3,
                "cost_iron_penny": 5,
                "bonus_armor": 1,
            },

            {
                "name": "Pantalones de Tela",
                "description": "Unos pantalones hechos de tela cómoda. Proporciona cobertura ligera para las piernas.",
                "item_type": "LGS",
                "rarity": "COM",
                "allowed_classes": ["WIZ", "SOR", "DRD", "WLK"],
                "cost_ardite": 3,
                "cost_iron_penny": 5,
                "bonus_armor": 1,
            },

            {
                "name": "Botas de Tela",
                "description": "Unas botas hechas de tela cómoda. Proporciona cobertura ligera para los pies.",
                "item_type": "FET",
                "rarity": "COM",
                "allowed_classes": ["WIZ", "SOR", "DRD", "WLK"],
                "cost_ardite": 2,
                "cost_iron_penny": 5,
                "bonus_armor": 1,
            },

            {
                "name": "Guantes de Tela",
                "description": "Unos guantes hechos de tela cómoda. Proporciona cobertura ligera para las manos.",
                "item_type": "HND",
                "rarity": "COM",
                "allowed_classes": ["WIZ", "SOR", "DRD", "WLK"],
                "cost_ardite": 2,
                "cost_iron_penny": 5,
                "bonus_armor": 1,
            },

            # CONJUNTO DE ARMADURA DE CUERO ACOLCHADO (COMÚN)

            {
                "name": "Gorro de Cuero Acolchado",
                "description": "Un gorro hecho de cuero acolchado. Es cómodo y protegido.",
                "item_type": "HED",
                "rarity": "COM",
                "allowed_classes": ["ROG", "RGR", "BRD", "MNK"],
                "cost_ardite": 2,
                "cost_iron_penny": 8,
                "bonus_armor": 1,
            },

            {
                "name": "Atuendo de Cuero Acolchado",
                "description": "Un atuendo hecho de cuero acolchado. Es cómodo y protegido.",
                "item_type": "TRS",
                "rarity": "COM",
                "allowed_classes": ["ROG", "RGR", "BRD", "MNK"],
                "cost_ardite": 3,
                "cost_iron_penny": 8,
                "bonus_armor": 1,
            },

            {
                "name": "Pantalones de Cuero Acolchado",
                "description": "Unos pantalones hechos de cuero acolchado. Son cómodos y protegidos.",
                "item_type": "LGS",
                "rarity": "COM",
                "allowed_classes": ["ROG", "RGR", "BRD", "MNK"],
                "cost_ardite": 3,
                "cost_iron_penny": 8,
                "bonus_armor": 1,
            },

            {
                "name": "Botas de Cuero Acolchado",
                "description": "Unas botas hechas de cuero acolchado. Son cómodas y protegidas.",
                "item_type": "FET",
                "rarity": "COM",
                "allowed_classes": ["ROG", "RGR", "BRD", "MNK"],
                "cost_ardite": 2,
                "cost_iron_penny": 8,
                "bonus_armor": 1,
            },

            {
                "name": "Guantes de Cuero Acolchado",
                "description": "Unos guantes hechos de cuero acolchado. Son cómodos y protegidos.",
                "item_type": "HND",
                "rarity": "COM",
                "allowed_classes": ["ROG", "RGR", "BRD", "MNK"],
                "cost_ardite": 2,
                "cost_iron_penny": 8,
                "bonus_armor": 1,
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
