INTEL = [
    {
        "id": "INC-2024-0341",
        "date": "14 NOV 2024 | 0220 HRS",
        "sector": "Tawang, Arunachal Pradesh",
        "grid": "4482-N",
        "type": "LAC patrol confrontation",
        "summary": "4 Corps patrol reported standoff with PLA unit at Yangtse river bend. Disengaged per protocol. No casualties.",
        "threat_contribution": "ELEVATED",
        "source": "4 Corps Forward HQ"
    },
    {
        "id": "INC-2024-0289",
        "date": "02 OCT 2024 | 1845 HRS",
        "sector": "Depsang Plains, Ladakh",
        "grid": "3371-W",
        "type": "Aerial intrusion — UAV",
        "summary": "Unidentified UAV tracked entering Indian airspace 2.3km. Turned back after IAF Heron scramble. Origin unconfirmed.",
        "threat_contribution": "GUARDED",
        "source": "IAF Forward Base Leh"
    },
    {
        "id": "INC-2024-0301",
        "date": "21 OCT 2024 | 0415 HRS",
        "sector": "Gurez Valley, J&K",
        "grid": "2291-E",
        "type": "Cross-border infiltration attempt",
        "summary": "BSF thermal imaging detected 3-man team attempting LoC crossing. Team repelled. One apprehended.",
        "threat_contribution": "ELEVATED",
        "source": "BSF Sector HQ Gurez"
    },
    {
        "id": "INC-2024-0318",
        "date": "08 NOV 2024 | 2340 HRS",
        "sector": "Arabian Sea, EEZ boundary",
        "grid": "SEA-77E",
        "type": "Unidentified submarine contact",
        "summary": "P-8I Poseidon detected submerged contact 40nm from EEZ boundary. Contact lost after 18 mins. Origin unconfirmed.",
        "threat_contribution": "HIGH",
        "source": "Western Naval Command"
    },
    {
        "id": "INC-2024-0255",
        "date": "15 SEP 2024 | 1100 HRS",
        "sector": "Demchok, Ladakh",
        "grid": "3388-S",
        "type": "Infrastructure activity observed",
        "summary": "Satellite imagery confirmed new forward post construction 800m beyond claimed LAC position.",
        "threat_contribution": "ELEVATED",
        "source": "NTRO Analysis Cell"
    },
    {
        "id": "INC-2024-0210",
        "date": "28 AUG 2024 | 0630 HRS",
        "sector": "Barahoti, Uttarakhand",
        "grid": "1142-N",
        "type": "Unauthorised grazing / border probe",
        "summary": "ITBP patrol observed 12 individuals with livestock crossing traditional boundary. Escorted back. Considered low-level probe.",
        "threat_contribution": "GUARDED",
        "source": "ITBP Sector HQ Pithoragarh"
    },
    {
        "id": "INC-2024-0198",
        "date": "10 AUG 2024 | 2210 HRS",
        "sector": "Kupwara, J&K",
        "grid": "2188-W",
        "type": "Tunnel detection",
        "summary": "Army Corps of Engineers confirmed new tunnel bore 340m from LoC. Demolition team deployed. Tunnel neutralised.",
        "threat_contribution": "HIGH",
        "source": "15 Corps Engineering Wing"
    },
    {
        "id": "INC-2024-0177",
        "date": "22 JUL 2024 | 1530 HRS",
        "sector": "Bay of Bengal, Andaman sector",
        "grid": "SEA-93E",
        "type": "Vessel intrusion — EEZ violation",
        "summary": "Chinese research vessel Xiang Yang Hong 03 entered Indian EEZ without clearance. Coast Guard vessel INS Rajratan issued warning. Vessel withdrew.",
        "threat_contribution": "ELEVATED",
        "source": "Eastern Naval Command"
    },
    {
        "id": "INC-2024-0155",
        "date": "05 JUL 2024 | 0345 HRS",
        "sector": "Poonch, J&K",
        "grid": "2090-S",
        "type": "Ceasefire violation",
        "summary": "Small arms fire reported across LoC at Grid 2090-S. No casualties. BSF returned fire. Situation stabilised by 0420 HRS.",
        "threat_contribution": "ELEVATED",
        "source": "BSF DIG Poonch Range"
    },
    {
        "id": "INC-2024-0132",
        "date": "18 JUN 2024 | 1120 HRS",
        "sector": "Finger Area, Pangong Tso",
        "grid": "3490-E",
        "type": "Patrol standoff",
        "summary": "Indian and PLA patrols made face-off contact at Finger 4. Both sides held position for 6 hours. Disengaged per hotline communication.",
        "threat_contribution": "ELEVATED",
        "source": "14 Corps Forward HQ"
    }
]

def search_intel(query: str) -> list:
    query_lower = query.lower()
    keywords = query_lower.split()
    scored = []
    for item in INTEL:
        score = 0
        searchable = (item["sector"] + item["type"] + item["summary"] + item["grid"]).lower()
        for word in keywords:
            if word in searchable:
                score += 1
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [item for _, item in scored[:3]]
    return results if results else INTEL[:3]