# Inspection documentation

This document reprensent all the documentation around an Inspection and the json
object representing it.

## Inspection Json
```JSON
{
    "inspection_id": "inspection uuid",
    "owner_id": "Organization uuid",
    "company": {
        "id": "organization_information uuid",
        "name": "Company Name",
        "address": "Company Adress",
        "website": "www.company.website.com",
        "phone_number": "# ### ### ####"
    },
    "manufacturer": {
        "id": "organization_inforamtion uuid",
        "name": "manufacturer name",
        "address": "manufacturer address",
        "website": "www.website.com",
        "phone_number": "1-123-456-7890"
    },
    "product": {
        "k": 0.0,
        "n": 0.0,
        "p": 0.0,
        "id": "label_information_id",
        "npk": "0-0-0",
        "verified": false,
        "name": "Product/Fertilizer Name",
        "metrics": {
            "volume": {
                "unit": "Volume unit",
                "value": 0.0
            },
            "weight": [
                {
                    "unit": "weight unit",
                    "value": 0.0
                }
            ],
            "density": {
                "unit": "density unit",
                "value": 0.0
            }
        },
        "warranty": "Warranty text on the label",
        "lot_number": "lot_number on the label",
        "registration_number": "Registration Number (if there is one)"
    },
    "cautions": {
        "en": [
            "List of cautions",
            "on the Label"
        ],
        "fr": [
            "Liste d'avertissement ",
            "sur l'étiquette"
        ]
    },
    "first_aid": {
        "en": [
            "List of first_aid advice on the label"
        ],
        "fr": [
            "Liste des conseils de premier soins sur l'étiquette"
        ]
    },
    "ingredients": {
        "en": [
            {
                "name": "Ingredient Name",
                "unit": "Unit of the ingredient (if there is one)",
                "value": 0.0
            },
            {
                "name": "Other Ingredient",
                "unit": "%",
                "value": 0.0
            }
        ],
        "fr": [
            {
                "name": "Nom de l'ingrédient",
                "unit": "unité de l'ingrédient (si présente)",
                "value": 0.0
            },
            {
                "name": "Autre ingrédient",
                "unit": "%",
                "value": 0.0
            }
        ]
    },
    "instructions": {
        "en": [
            "1. List of instructions",
            "2. on the label"
        ],
        "fr": [
            "1. Liste d'instruction",
            "2. sur l'étiquette"
        ]
    },
    "micronutrients": {
        "en": [
            {
                "name": "MicroNutrient name on the label",
                "unit": "Unit (usually %)",
                "value": 0.0
            },
            {
                "name": "Zinc (Zn)",
                "unit": "%",
                "value": 0.0
            }
        ],
        "fr": [
            {
                "name": "nom du Micronutriment sur l'étiquette",
                "unit": "unité (normalement %)",
                "value": 0.0
            },
            {
                "name": "Zinc (Zn)",
                "unit": "%",
                "value": 0.05
            }
        ]
    },
    "specifications": {
        "en": [
            {
                "ph": 0.0,
                "humidity": 0.0,
                "solubility": 0.0
            }
        ],
        "fr": [
            {
                "ph": 0.0,
                "humidity": 0.0,
                "solubility": 0.0
            }
        ]
    },
    "guaranteed_analysis": [
        {
            "name": "Name of the element or compound_element",
            "unit": "%",
            "value": 0.0
        },
        {
            "name": "Phosphate (P2O5)",
            "unit": "%",
            "value": 20.0
        },
    ]
}

```