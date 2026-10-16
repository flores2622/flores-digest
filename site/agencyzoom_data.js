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
  "product_default": "{carrier}-{raw}"
};
