"""
Generates synthetic .ntriples demo data that mimics OpenPermID structure.
Run this once to populate the /data folder before launching the app.
"""

import os
import random

random.seed(42)

BASE = "<https://permid.org/"
RDF = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "<http://www.w3.org/2000/01/rdf-schema#"
OWL = "<http://www.w3.org/2002/07/owl#"
TR = "<https://permid.org/ontology/financial/"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


def uri(path):
    return f"<https://permid.org/{path}>"


def rdf_type():
    return f"{RDF}type>"


def rdfs_label():
    return f"{RDFS}label>"


def triple(s, p, o, literal=False):
    if literal:
        return f"{s} {p} {o} .\n"
    return f"{s} {p} {o} .\n"


def lit(value, lang="en"):
    return f'"{value}"@{lang}'


# ── CURRENCY ──────────────────────────────────────────────────────────────────
CURRENCIES = [
    ("USD", "US Dollar", "United States"),
    ("EUR", "Euro", "European Union"),
    ("GBP", "British Pound Sterling", "United Kingdom"),
    ("JPY", "Japanese Yen", "Japan"),
    ("CHF", "Swiss Franc", "Switzerland"),
    ("AUD", "Australian Dollar", "Australia"),
    ("CAD", "Canadian Dollar", "Canada"),
    ("CNY", "Chinese Yuan Renminbi", "China"),
    ("HKD", "Hong Kong Dollar", "Hong Kong"),
    ("SGD", "Singapore Dollar", "Singapore"),
    ("SEK", "Swedish Krona", "Sweden"),
    ("NOK", "Norwegian Krone", "Norway"),
    ("DKK", "Danish Krone", "Denmark"),
    ("NZD", "New Zealand Dollar", "New Zealand"),
    ("KRW", "South Korean Won", "South Korea"),
    ("INR", "Indian Rupee", "India"),
    ("BRL", "Brazilian Real", "Brazil"),
    ("MXN", "Mexican Peso", "Mexico"),
    ("ZAR", "South African Rand", "South Africa"),
    ("TRY", "Turkish Lira", "Turkey"),
]

CURRENCY_TYPE = f"{TR}Currency>"
ISO_PRED = f"{TR}isoCode>"
COUNTRY_PRED = f"{TR}issuingCountry>"
SYMBOL_PRED = f"{TR}currencySymbol>"
ACTIVE_PRED = f"{TR}isActive>"
DEPRECATED_PRED = f"{OWL}deprecated>"

SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CHF": "Fr",
    "AUD": "A$",
    "CAD": "C$",
    "CNY": "¥",
    "HKD": "HK$",
    "SGD": "S$",
    "SEK": "kr",
    "NOK": "kr",
    "DKK": "kr",
    "NZD": "NZ$",
    "KRW": "₩",
    "INR": "₹",
    "BRL": "R$",
    "MXN": "$",
    "ZAR": "R",
    "TRY": "₺",
}

with open(
    os.path.join(DATA_DIR, "OpenPermID-bulk-currency.ntriples"), "w", encoding="utf-8"
) as f:
    for code, name, country in CURRENCIES:
        s = uri(f"1-{code}")
        f.write(triple(s, rdf_type(), CURRENCY_TYPE))
        f.write(triple(s, rdfs_label(), lit(name), literal=True))
        f.write(triple(s, ISO_PRED, lit(code), literal=True))
        f.write(triple(s, COUNTRY_PRED, lit(country), literal=True))
        f.write(triple(s, SYMBOL_PRED, lit(SYMBOLS.get(code, code)), literal=True))
        f.write(triple(s, ACTIVE_PRED, lit("true"), literal=True))

print("✓ currency.ntriples")

# ── ASSET CLASS ───────────────────────────────────────────────────────────────
ASSET_CLASSES = [
    ("Equity", ["CommonStock", "PreferredStock", "ETF", "ClosedEndFund"]),
    (
        "FixedIncome",
        ["GovernmentBond", "CorporateBond", "MunicipalBond", "ConvertibleBond"],
    ),
    ("Derivative", ["Future", "Option", "Swap", "ForwardContract"]),
    ("Cash", ["CashDeposit", "MoneyMarket", "Treasury"]),
    ("Alternative", ["Commodity", "RealEstate", "HedgeFund", "PrivateEquity"]),
    ("MixedAllocation", ["BalancedFund", "MultiAsset"]),
]

ASSET_CLASS_TYPE = f"{TR}AssetClass>"
ASSET_TYPE_TYPE = f"{TR}AssetType>"
BELONGS_PRED = f"{TR}belongsToAssetClass>"
COUNT_PRED = f"{TR}instrumentCount>"

with open(os.path.join(DATA_DIR, "OpenPermID-bulk-assetClass.ntriples"), "w") as f:
    for ac_name, subtypes in ASSET_CLASSES:
        ac_uri = uri(f"ac-{ac_name}")
        f.write(triple(ac_uri, rdf_type(), ASSET_CLASS_TYPE))
        f.write(triple(ac_uri, rdfs_label(), lit(ac_name), literal=True))
        count = random.randint(500, 5000)
        f.write(triple(ac_uri, COUNT_PRED, lit(str(count)), literal=True))
        for st in subtypes:
            st_uri = uri(f"at-{st}")
            f.write(triple(st_uri, rdf_type(), ASSET_TYPE_TYPE))
            f.write(triple(st_uri, rdfs_label(), lit(st), literal=True))
            f.write(triple(st_uri, BELONGS_PRED, ac_uri))

print("✓ assetClass.ntriples")

# ── INDUSTRY ──────────────────────────────────────────────────────────────────
SECTORS = [
    "Technology",
    "Financials",
    "Healthcare",
    "Energy",
    "ConsumerDiscretionary",
    "ConsumerStaples",
    "Industrials",
    "Materials",
    "Utilities",
    "RealEstate",
    "CommunicationServices",
]

INDUSTRIES_BY_SECTOR = {
    "Technology": [
        "Software",
        "Hardware",
        "Semiconductors",
        "ITServices",
        "InternetRetail",
    ],
    "Financials": [
        "Banking",
        "Insurance",
        "AssetManagement",
        "CapitalMarkets",
        "REITFinance",
    ],
    "Healthcare": [
        "Pharmaceuticals",
        "Biotechnology",
        "MedicalDevices",
        "HealthcareServices",
    ],
    "Energy": [
        "OilGasExploration",
        "IntegratedOilGas",
        "RenewableEnergy",
        "EnergyEquipment",
    ],
    "ConsumerDiscretionary": [
        "Automotive",
        "RetailApparel",
        "Hotels",
        "MediaEntertainment",
    ],
    "ConsumerStaples": [
        "FoodBeverage",
        "Tobacco",
        "HouseholdProducts",
        "PersonalProducts",
    ],
    "Industrials": ["Aerospace", "DefenseContractors", "Machinery", "Transportation"],
    "Materials": ["Chemicals", "Metals", "Mining", "Packaging", "Construction"],
    "Utilities": [
        "ElectricUtilities",
        "GasUtilities",
        "WaterUtilities",
        "MultiUtilities",
    ],
    "RealEstate": ["CommercialREIT", "ResidentialREIT", "DiversifiedREIT"],
    "CommunicationServices": ["Telecom", "MediaBroadcast", "InteractiveMedia"],
}

SECTOR_TYPE = f"{TR}BusinessSector>"
INDUSTRY_TYPE = f"{TR}Industry>"
PART_OF_PRED = f"{TR}isPartOf>"
HAS_IND_PRED = f"{TR}hasIndustry>"

with open(os.path.join(DATA_DIR, "OpenPermID-bulk-industry.ntriples"), "w") as f:
    for sector in SECTORS:
        s_uri = uri(f"sector-{sector}")
        f.write(triple(s_uri, rdf_type(), SECTOR_TYPE))
        f.write(triple(s_uri, rdfs_label(), lit(sector), literal=True))
        for ind in INDUSTRIES_BY_SECTOR.get(sector, []):
            i_uri = uri(f"ind-{ind}")
            f.write(triple(i_uri, rdf_type(), INDUSTRY_TYPE))
            f.write(triple(i_uri, rdfs_label(), lit(ind), literal=True))
            f.write(triple(i_uri, PART_OF_PRED, s_uri))
            f.write(triple(s_uri, HAS_IND_PRED, i_uri))

print("✓ industry.ntriples")

# ── ORGANIZATION ──────────────────────────────────────────────────────────────
ORG_NAMES = [
    ("Apple Inc", "Technology", "US", "PublicCompany"),
    ("Microsoft Corporation", "Technology", "US", "PublicCompany"),
    ("JPMorgan Chase", "Financials", "US", "PublicCompany"),
    ("Goldman Sachs", "Financials", "US", "PublicCompany"),
    ("HSBC Holdings", "Financials", "GB", "PublicCompany"),
    ("Deutsche Bank", "Financials", "DE", "PublicCompany"),
    ("Toyota Motor", "ConsumerDiscretionary", "JP", "PublicCompany"),
    ("Samsung Electronics", "Technology", "KR", "PublicCompany"),
    ("Nestlé SA", "ConsumerStaples", "CH", "PublicCompany"),
    ("Shell plc", "Energy", "GB", "PublicCompany"),
    ("BlackRock Inc", "Financials", "US", "PublicCompany"),
    ("Berkshire Hathaway", "Financials", "US", "PublicCompany"),
    ("Johnson & Johnson", "Healthcare", "US", "PublicCompany"),
    ("Pfizer Inc", "Healthcare", "US", "PublicCompany"),
    ("ExxonMobil", "Energy", "US", "PublicCompany"),
    ("Alphabet Inc", "Technology", "US", "PublicCompany"),
    ("Amazon.com Inc", "ConsumerDiscretionary", "US", "PublicCompany"),
    ("Tesla Inc", "ConsumerDiscretionary", "US", "PublicCompany"),
    ("Meta Platforms", "CommunicationServices", "US", "PublicCompany"),
    ("LVMH", "ConsumerDiscretionary", "FR", "PublicCompany"),
    ("Siemens AG", "Industrials", "DE", "PublicCompany"),
    ("BP plc", "Energy", "GB", "PublicCompany"),
    ("Alibaba Group", "ConsumerDiscretionary", "CN", "PublicCompany"),
    ("Tencent Holdings", "CommunicationServices", "CN", "PublicCompany"),
    ("Roche Holding", "Healthcare", "CH", "PublicCompany"),
    ("Venture Capital Fund A", "Financials", "US", "PrivateFund"),
    ("PE Partners Ltd", "Financials", "GB", "PrivateFund"),
    ("State Street Corp", "Financials", "US", "PublicCompany"),
    ("UBS Group", "Financials", "CH", "PublicCompany"),
    ("BNP Paribas", "Financials", "FR", "PublicCompany"),
]

ORG_TYPE_URI = f"{TR}Organization>"
IND_PRED = f"{TR}hasIndustrySector>"
COUNTRY_PRED2 = f"{TR}domicileCountry>"
STATUS_PRED = f"{TR}organizationStatusCode>"
ORG_TYPE_PRED = f"{TR}organizationType>"
FOUNDED_PRED = f"{TR}foundedYear>"

with open(os.path.join(DATA_DIR, "OpenPermID-bulk-organization.ntriples"), "w") as f:
    for i, (name, sector, country, org_type) in enumerate(ORG_NAMES):
        s = uri(f"org-{i+1:04d}")
        f.write(triple(s, rdf_type(), ORG_TYPE_URI))
        f.write(triple(s, rdfs_label(), lit(name), literal=True))
        f.write(triple(s, IND_PRED, uri(f"sector-{sector}")))
        f.write(triple(s, COUNTRY_PRED2, lit(country), literal=True))
        f.write(triple(s, STATUS_PRED, lit("Active"), literal=True))
        f.write(triple(s, ORG_TYPE_PRED, lit(org_type), literal=True))
        f.write(
            triple(s, FOUNDED_PRED, lit(str(random.randint(1850, 2010))), literal=True)
        )

print("✓ organization.ntriples")

# ── PERSON ────────────────────────────────────────────────────────────────────
PEOPLE = [
    ("Tim Cook", "CEO", "org-0001"),
    ("Satya Nadella", "CEO", "org-0002"),
    ("Jamie Dimon", "CEO", "org-0003"),
    ("David Solomon", "CEO", "org-0004"),
    ("Noel Quinn", "CEO", "org-0005"),
    ("Christian Sewing", "CEO", "org-0006"),
    ("Koji Sato", "CEO", "org-0007"),
    ("Jong-Hee Han", "CEO", "org-0008"),
    ("Mark Schneider", "CEO", "org-0009"),
    ("Wael Sawan", "CEO", "org-0010"),
    ("Larry Fink", "CEO", "org-0011"),
    ("Warren Buffett", "Chairman", "org-0012"),
    ("Sundar Pichai", "CEO", "org-0016"),
    ("Andy Jassy", "CEO", "org-0017"),
    ("Elon Musk", "CEO", "org-0018"),
    ("Mark Zuckerberg", "CEO", "org-0019"),
    ("Bernard Arnault", "Chairman", "org-0020"),
    ("Roland Busch", "CEO", "org-0021"),
    ("Murray Auchincloss", "CEO", "org-0022"),
    ("Eddie Wu", "CEO", "org-0023"),
    ("Pony Ma", "Chairman", "org-0024"),
    ("Thomas Schinecker", "CEO", "org-0025"),
]

PERSON_TYPE = f"{TR}Person>"
ROLE_PRED = f"{TR}hasRole>"
EMPLOYER_PRED = f"{TR}employedBy>"
GENDER_PRED = f"{TR}gender>"

with open(os.path.join(DATA_DIR, "OpenPermID-bulk-person.ntriples"), "w") as f:
    for i, (name, role, org) in enumerate(PEOPLE):
        s = uri(f"person-{i+1:04d}")
        f.write(triple(s, rdf_type(), PERSON_TYPE))
        f.write(triple(s, rdfs_label(), lit(name), literal=True))
        f.write(triple(s, ROLE_PRED, lit(role), literal=True))
        f.write(triple(s, EMPLOYER_PRED, uri(org)))
        f.write(triple(s, GENDER_PRED, lit("Male"), literal=True))

print("✓ person.ntriples")

# ── QUOTE ─────────────────────────────────────────────────────────────────────
EXCHANGES = [
    "NYSE",
    "NASDAQ",
    "LSE",
    "TSE",
    "HKEX",
    "SSE",
    "Euronext",
    "ASX",
    "SGX",
    "BSE",
]
QUOTE_TYPES = ["PrimaryQuote", "SecondaryQuote", "Delisted"]

with open(os.path.join(DATA_DIR, "OpenPermID-bulk-quote.ntriples"), "w") as f:
    for i in range(60):
        s = uri(f"quote-{i+1:04d}")
        qt = QUOTE_TYPES[i % len(QUOTE_TYPES)]
        exch = EXCHANGES[i % len(EXCHANGES)]
        ccy = CURRENCIES[i % len(CURRENCIES)][0]
        org_id = (i % len(ORG_NAMES)) + 1
        f.write(triple(s, rdf_type(), f"{TR}{qt}>"))
        f.write(triple(s, rdfs_label(), lit(f"Quote-{i+1:04d}"), literal=True))
        f.write(triple(s, f"{TR}listedOn>", lit(exch), literal=True))
        f.write(triple(s, f"{TR}quoteCurrency>", uri(f"1-{ccy}")))
        f.write(triple(s, f"{TR}quotedOrganization>", uri(f"org-{org_id:04d}")))
        f.write(
            triple(
                s,
                f"{TR}lotSize>",
                lit(str(random.choice([1, 10, 100, 1000]))),
                literal=True,
            )
        )

print("✓ quote.ntriples")

# ── INSTRUMENT ────────────────────────────────────────────────────────────────
INST_TYPES = [
    "Equity",
    "Bond",
    "ETF",
    "Option",
    "Future",
    "Swap",
    "MutualFund",
    "Warrant",
]

with open(os.path.join(DATA_DIR, "OpenPermID-bulk-instrument.ntriples"), "w") as f:
    for i in range(80):
        s = uri(f"inst-{i+1:04d}")
        it = INST_TYPES[i % len(INST_TYPES)]
        ccy = CURRENCIES[i % len(CURRENCIES)][0]
        org_id = (i % len(ORG_NAMES)) + 1
        ac = ASSET_CLASSES[i % len(ASSET_CLASSES)][0]
        f.write(triple(s, rdf_type(), f"{TR}Instrument>"))
        f.write(triple(s, rdfs_label(), lit(f"Instrument-{i+1:04d}"), literal=True))
        f.write(triple(s, f"{TR}instrumentType>", lit(it), literal=True))
        f.write(triple(s, f"{TR}denominatedIn>", uri(f"1-{ccy}")))
        f.write(triple(s, f"{TR}issuedBy>", uri(f"org-{org_id:04d}")))
        f.write(triple(s, f"{TR}hasAssetClass>", uri(f"ac-{ac}")))
        f.write(triple(s, f"{TR}isin>", lit(f"XX{i+1:010d}"), literal=True))

print("✓ instrument.ntriples")
print("\n✅ All demo data files created successfully in /data/")
