from enum import Enum

class CountryGroups(Enum):
    formip_regions = {
        "Africa": [
            "AGO", "ARE", "BDI", "BEN", "BFA", "BHR", "BWA", "CAF", "CIV", "CMR", "COD", "COG", "COM", "CPV", "DJI",
            "DZA", "EGY", "ERI", "ESH", "ETH", "GAB", "GHA", "GIN", "GMB", "GNB", "GNQ", "IRN", "IRQ", "ISR", "JOR",
            "KEN", "KWT", "LBN", "LBR", "LBY", "LSO", "MAR", "MDG", "MLI", "MOZ", "MRT", "MUS", "MWI", "MYT", "NAM",
            "NER", "NGA", "OMN", "PSE", "QAT", "REU", "RWA", "SAU", "SDN", "SEN", "SHN", "SLE", "SOM", "SSD", "STP",
            "SWZ", "SYC", "SYR", "TCD", "TGO", "TUN", "TUR", "TZA", "UGA", "YEM", "ZAF", "ZMB", "ZWE"
        ],
        "Asia": [
            "AFG", "ASM", "AUS", "BGD", "BRN", "BTN", "CHN", "COK", "FJI", "FSM", "GUM", "IDN", "IND", "JPN", "KHM",
            "KIR", "KOR", "LAO", "LKA", "MDV", "MHL", "MMR", "MNG", "MNP", "MYS", "NCL", "NFK", "NIU", "NPL", "NRU",
            "NZL", "PAK", "PCN", "PHL", "PLW", "PNG", "PRK", "PYF", "SGP", "SLB", "THA", "TKL", "TLS", "TON", "TUV",
            "VNM", "VUT", "WLF", "WSM"
        ],
        "Europe": [
            "ALB", "AND", "AUT", "BGR", "BIH", "BEL", "CHE", "CZE", "DEU", "DNK", "ESP", "EST", "FIN", "FRA", "FRO",
            "GBR", "GGY", "GIB", "GRC", "HRV", "HUN", "IMN", "IRL", "ISL", "ITA", "JEY", "LIE", "LTU", "LUX", "LVA",
            "MCO", "MKD", "MLT", "MNE", "NLD", "NOR", "POL", "PRT", "ROU", "SJM", "SMR", "SRB", "SVK", "SVN", "SWE",
            "VAT"
        ],
        "Former Soviet Union": [
            "ARM", "AZE", "BLR", "GEO", "KAZ", "KGZ", "MDA", "RUS", "TJK", "TKM", "UZB", "UKR"
        ],
        "Latin America": [
            "ABW", "AIA", "ARG", "ATG", "BOL", "BES", "BHS", "BLM", "BLZ", "BMU", "BRA", "BRB", "CHL", "COL", "CRI",
            "CUB", "CUW", "CYM", "DMA", "DOM", "ECU", "FLK", "GLP", "GRD", "GTM", "GUF", "GUY", "HND", "HTI", "JAM",
            "KNA", "LCA", "MAF", "MEX", "MSR", "MTQ", "NIC", "PAN", "PER", "PRI", "PRY", "SLV", "SPM", "SUR", "SXM",
            "TCA", "TTO", "URY", "VCT", "VEN", "VGB", "VIR"
        ],
        "North America": [
            "CAN", "USA", "GRL"
        ]
    }