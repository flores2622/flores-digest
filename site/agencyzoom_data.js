// WRITTEN BY `python3 agencyzoom.py --write-js` FROM agencyzoom.json -- do not edit.
// The Worker's copy of the carriers and the Sales sheet's product names: see agencyzoom.py.
export default {
  "carriers": {
    "484668": "Farmers",
    "484654": "Farmers",
    "1030958": "Farmers",
    "2448048": "Farmers",
    "186": "BW",
    "2448054": "BW",
    "102": "Foremost",
    "262": "Foremost",
    "2448051": "Foremost"
  },
  "product_rules": [
    {
      "carrier": "BW",
      "match": "auto",
      "name": "BW-Auto"
    },
    {
      "carrier": "BW",
      "name": "BW-{raw}"
    },
    {
      "match": "auto",
      "name": "{carrier}-Auto"
    },
    {
      "carrier": "Foremost",
      "match": "mobile|manufactured",
      "name": "Foremost-MH"
    },
    {
      "carrier": "Foremost",
      "match": "landlord|dp\\d|dwelling",
      "name": "Foremost-Landlord"
    },
    {
      "carrier": "Foremost",
      "match": "atv|motorcycle|trailer|boat|watercraft|motor home|\\brv\\b|golf cart|toy",
      "name": "Foremost-Toys"
    },
    {
      "carrier": "Foremost",
      "match": "vacant",
      "name": "Foremost-Vacant"
    },
    {
      "carrier": "Foremost",
      "match": "home|ho-?\\d",
      "name": "Foremost-Home"
    },
    {
      "carrier": "Farmers",
      "match": "homeowner|^home$|ho-?\\d",
      "name": "Farmers-Home"
    },
    {
      "carrier": "Farmers",
      "match": "term|life",
      "name": "Farmers-Life"
    }
  ],
  "product_default": "{carrier}-{raw}",
  "sheet": {
    "products": [
      {
        "carrier": "Farmers",
        "options": [
          {
            "value": "Farmers-Auto",
            "types": [
              "Auto",
              "Commercial Auto",
              "Standard Auto"
            ]
          },
          {
            "value": "Farmers-Commercial BOP",
            "types": [
              "Commercial BOP"
            ]
          },
          {
            "value": "Farmers-Commercial BOP Property",
            "types": [
              "Commercial BOP Property"
            ]
          },
          {
            "value": "Farmers-Commercial GL",
            "types": [
              "Commercial GL"
            ]
          },
          {
            "value": "Farmers-Commercial Property",
            "types": [
              "Commercial Property"
            ]
          },
          {
            "value": "Farmers-Commercial Umbrella",
            "types": [
              "Commercial Umbrella"
            ]
          },
          {
            "value": "Farmers-Condo",
            "types": [
              "Condo"
            ]
          },
          {
            "value": "Farmers-Course of Construction",
            "types": [
              "Course of Construction"
            ]
          },
          {
            "value": "Farmers-Home",
            "types": [
              "Home",
              "Homeowners"
            ]
          },
          {
            "value": "Farmers-Landlord",
            "types": [
              "Landlord"
            ]
          },
          {
            "value": "Farmers-Life",
            "types": [
              "10 year term",
              "20 year term",
              "30  year term",
              "Index Universal Life",
              "Individual Life",
              "Universal Life",
              "Variable Universal Life",
              "Whole Life"
            ]
          },
          {
            "value": "Farmers-Motorcycle",
            "types": [
              "Motorcycle"
            ]
          },
          {
            "value": "Farmers-Renters",
            "types": [
              "Renters"
            ]
          },
          {
            "value": "Farmers-Secondary Home",
            "types": [
              "Secondary Home"
            ]
          },
          {
            "value": "Farmers-Umbrella",
            "types": [
              "Umbrella"
            ]
          },
          {
            "value": "Farmers-Workers Comp",
            "types": [
              "Workers Comp"
            ]
          }
        ]
      },
      {
        "carrier": "BW",
        "options": [
          {
            "value": "BW-Auto",
            "types": [
              "Auto",
              "Commercial Auto",
              "Non Owner Auto"
            ]
          }
        ]
      },
      {
        "carrier": "Foremost",
        "options": [
          {
            "value": "Foremost-Home",
            "types": [
              "HO-3",
              "Home",
              "Seasonal Home",
              "Secondary Home"
            ]
          },
          {
            "value": "Foremost-Landlord",
            "types": [
              "DP1 - Property",
              "Landlord"
            ]
          },
          {
            "value": "Foremost-MH",
            "types": [
              "Manufactured Home",
              "Mobile Home"
            ]
          },
          {
            "value": "Foremost-Short-Term Rental",
            "types": [
              "Short-Term Rental"
            ]
          },
          {
            "value": "Foremost-Toys",
            "types": [
              "ATV",
              "Boat",
              "Golf Cart",
              "Motor Home",
              "Motorcycle",
              "Personal Watercraft",
              "RV",
              "Trailer"
            ]
          },
          {
            "value": "Foremost-Vacant",
            "types": [
              "Vacant"
            ]
          },
          {
            "value": "Foremost-Vacation",
            "types": [
              "Vacation"
            ]
          }
        ]
      },
      {
        "carrier": "Other",
        "options": [
          {
            "value": "Auto",
            "types": [
              "Auto"
            ]
          },
          {
            "value": "Bond",
            "types": [
              "Bond"
            ]
          },
          {
            "value": "Builders Risk",
            "types": [
              "Builders Risk"
            ]
          },
          {
            "value": "Classic Auto",
            "types": [
              "Classic Auto"
            ]
          },
          {
            "value": "Commercial Auto",
            "types": [
              "Commercial Auto"
            ]
          },
          {
            "value": "Commercial BOP",
            "types": [
              "Commercial BOP"
            ]
          },
          {
            "value": "Commercial BOP Liability",
            "types": [
              "Commercial BOP Liability"
            ]
          },
          {
            "value": "Commercial GL",
            "types": [
              "Commercial GL"
            ]
          },
          {
            "value": "Commercial Package",
            "types": [
              "Commercial Package"
            ]
          },
          {
            "value": "Dealer Bond",
            "types": [
              "Dealer Bond"
            ]
          },
          {
            "value": "Driver License MX Liability",
            "types": [
              "Driver License MX Liability"
            ]
          },
          {
            "value": "General Liability",
            "types": [
              "General Liability"
            ]
          },
          {
            "value": "Landlord",
            "types": [
              "Landlord"
            ]
          },
          {
            "value": "Mexico Auto Policy",
            "types": [
              "Mexico Auto Policy"
            ]
          },
          {
            "value": "Professional Liability",
            "types": [
              "Professional Liability"
            ]
          },
          {
            "value": "Standard Auto",
            "types": [
              "Standard Auto"
            ]
          },
          {
            "value": "Umbrella",
            "types": [
              "Umbrella"
            ]
          },
          {
            "value": "Workers Comp",
            "types": [
              "Workers Comp"
            ]
          }
        ]
      }
    ],
    "terms": [
      {
        "value": "6mo",
        "label": "6 months"
      },
      {
        "value": "12mo",
        "label": "12 months"
      },
      {
        "value": "120mo",
        "label": "10 years (term life)"
      },
      {
        "value": "240mo",
        "label": "20 years (term life)"
      },
      {
        "value": "360mo",
        "label": "30 years (term life)"
      }
    ]
  }
};
