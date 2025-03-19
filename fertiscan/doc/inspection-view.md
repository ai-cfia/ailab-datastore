# Inspection documentation

This document reprensent what an Inspection Model is

## Inspection Model Example

```JSON
{
    "inspection_id": "inspection uuid",
    "container_id": "container_uuid",
    "folder_id": "folder_uuid",
    "inspector_id": "Organization uuid",
    "upload_date": "timestamp of the creation of this inspection",
    "updated_at": "timestamp of the latest update on this inspection",
    "organizations": [
      {
          "name": "Name of company",
          "address": "address of company",
          "website": "www.website.com",
          "phone_number": "+1 800 000 0111",
          "edited": false,
          "is_main_contact": true
      },
      {
          "name": "Another company",
          "address": "Address of second company",
          "website": "www.website2.com",
          "phone_number": "+1 444 555 0123",
          "edited": false,
          "is_main_contact": false
      }
    ],
    "product": {
        "name" : "Name of the fertilizer",
        "label_id": "label_information id",
        "k": 0.0,
        "n": 0.0,
        "p": 0.0,
        "npk": "0-0-0",
        "warranty": "Warranty of the product (not tracked)",
        "record_keeping": false,
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
        "registration_numbers": [{
            "registration_number": "F12345678",
            "is_an_ingredient": false,
            "edited": false
        }],
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
    "guaranteed_analysis":{
        "title": {
            "en": "Guaranteed Analysis",
            "fr": "Analyse Garantie"
        },
        "is_minimal" : false,
        "en":[
        {
            "name": "Name of the element or compound_element",
            "unit": "%",
            "value": 0.0
        },],
        "fr":[
        {
            "name": "Phosphate (P2O5)",
            "unit": "%",
            "value": 20.0
        },]
    }
}

```
