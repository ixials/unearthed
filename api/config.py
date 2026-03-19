CHAR_MAP = {
    # Turkish
    'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u',
    'İ': 'I', 'Ğ': 'G', 'Ş': 'S', 'Ç': 'C', 'Ö': 'O', 'Ü': 'U',
    # Polish
    'ł': 'l', 'Ł': 'L', 'ń': 'n', 'ź': 'z', 'ż': 'z', 'ą': 'a', 'ę': 'e', 'ś': 's',
    # Scandinavian
    'ø': 'o', 'Ø': 'O', 'å': 'a', 'Å': 'A', 'æ': 'ae', 'Æ': 'AE',
    # German
    'ß': 'ss',
    # Icelandic
    'þ': 'th', 'Þ': 'Th', 'ð': 'd', 'Ð': 'D',
    # Romanian
    'ț': 't', 'ș': 's', 'Ț': 'T', 'Ș': 'S',
    # Czech/Slovak
    'ď': 'd', 'ť': 't', 'ľ': 'l', 'ĺ': 'l', 'ŕ': 'r',
    # Croatian/Serbian
    'đ': 'd', 'Đ': 'D',
    # Vietnamese
    'đ': 'd', 'Đ': 'D',
    'ơ': 'o', 'Ơ': 'O',
    'ư': 'u', 'Ư': 'U',
    'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
    'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
    'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
    'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
    'ỳ': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
    'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
    'ọ': 'o', 'ỏ': 'o',
    'ụ': 'u', 'ủ': 'u',
    'ạ': 'a', 'ả': 'a', 'ã': 'a',
    'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
    'ợ': 'o', 'ị': 'i',
    # Greek
    'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'e',
    'θ': 'th', 'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x',
    'ο': 'o', 'π': 'p', 'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'u', 'φ': 'f',
    'χ': 'ch', 'ψ': 'ps', 'ω': 'o',
    # Latvian
    'ā': 'a', 'ē': 'e', 'ī': 'i', 'ū': 'u', 'ģ': 'g', 'ķ': 'k', 'ļ': 'l', 'ņ': 'n', 'ŗ': 'r',
    # Lithuanian
    'ą': 'a', 'č': 'c', 'ę': 'e', 'ė': 'e', 'į': 'i', 'š': 's', 'ų': 'u', 'ū': 'u', 'ž': 'z',
    # Hungarian
    'ő': 'o', 'ű': 'u',
    # Maltese
    'ħ': 'h', 'Ħ': 'H',
    # Welsh
    'ŵ': 'w', 'ŷ': 'y',
}

CATEGORY_KEYWORDS = {
    "Artifact": [
        "artifact", "pottery", "ceramic", "tool", "jewelry",
        "coin", "figurine", "mask", "tablet", "inscription",
        "sword", "scroll", "vial", "textile", "mosaic", "headdress", 
        "armor", "helmet"
    ],
    "Ruins": [
        "ruins", "temple", "palace", "fortress", "fortification,"
        "wall", "structure", "settlement", "city", "building", 
        "monument", "castle", "villa", "forum", "church", "cathedral"
    ],
    "Burial": [
        "burial", "tomb", "grave", "cemetery", "sarcophagus",
        "coffin", "skeleton", "remains", "mummy", "bone"
    ],
    "Fossil": [
        "fossil", "dinosaur", "prehistoric", "vertebra",
        "bone", "paleontologist", "species", "skull", "extinct", 
        "million"
    ],
    "Shipwreck": [
        "shipwreck", "wreck", "vessel", "ship", "boat",
        "maritime", "sunk", "cargo"
    ]
}

DISCOVERY_KEYWORDS = {
    "found", "discovered", "unearthed", "excavated", "uncovered", 
    "revealed", "recovered", "located", "identified", "excavation",
    "buried", "dug", "tomb", "ruins", "artifact", "skeleton",
    "burial", "necropolis", "temple", "site", "dig"
}

DESC_BLACKLIST = [ "appeared first on ", "the post ", "[...]" ]

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "of", "for", "to", "from", "and",
    "with", "near", "after", "before", "new", "ancient", "old"
}

QUERY = (
    "(archaeologist OR paleontologist OR archaeology OR paleontology)" 
    "AND" 
    "(ancient OR excavation OR fossil OR artifact OR relic OR shipwreck"
    " OR ruins OR tomb OR burial OR mosaic OR inscription OR pottery"
    " OR civilization OR castle OR fortress OR textile OR sword OR jewelry)"
    " AND "
    "(discovery OR discover OR discovered OR unearth OR unearthed OR uncover OR uncovered"
    " OR excavate OR excavated OR reveal OR revealed OR recover OR recovered OR found)"
    )