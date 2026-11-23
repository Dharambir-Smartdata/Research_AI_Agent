"""
Script to generate authentic educational dummy PDFs for all 8 UPSC subjects:
- 2 study material PDFs per subject
- 1 PYQ PDF per subject with UPSC questions and answer keys
"""
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE_UPSC_DIR = Path(__file__).resolve().parent / "UPSC"

def create_pdf(file_path: Path, title: str, subtitle: str, sections: list):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4338ca'),
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8,
    )
    
    story = []
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=12))
    
    for heading, paragraphs in sections:
        if heading:
            story.append(Paragraph(heading, heading_style))
        for p in paragraphs:
            story.append(Paragraph(p, body_style))
        story.append(Spacer(1, 6))
        
    doc.build(story)
    print(f"Generated: {file_path.relative_to(BASE_UPSC_DIR.parent)}")

SUBJECT_DATA = {
    "Indian_Polity": {
        "study": [
            (
                "constitutional_framework.pdf",
                "UPSC Civil Services - Indian Polity & Governance",
                "Module 01: Constitutional Framework & Fundamental Rights",
                [
                    ("1. Preamble & Basic Structure Doctrine", [
                        "The Preamble to the Indian Constitution declares India to be a Sovereign, Socialist, Secular, Democratic Republic. It guarantees Justice (social, economic, and political), Liberty of thought, expression, belief, faith and worship, Equality of status and of opportunity, and Fraternity assuring the dignity of the individual.",
                        "In the landmark Kesavananda Bharati case (1973), the Supreme Court ruled that Article 368 does not enable Parliament to alter the 'Basic Structure' of the Constitution. Essential elements include supremacy of the Constitution, republican and democratic form of government, secular character, separation of powers, and judicial review.",
                        "The 42nd Constitutional Amendment Act of 1976 added three words to the Preamble: 'Socialist', 'Secular', and 'Integrity'."
                    ]),
                    ("2. Fundamental Rights (Articles 12 to 35)", [
                        "Part III of the Constitution confers justiciable Fundamental Rights. Key categories include Right to Equality (Articles 14-18), Right to Freedom (Articles 19-22), Right against Exploitation (Articles 23-24), Right to Freedom of Religion (Articles 25-28), Cultural and Educational Rights (Articles 29-30), and Right to Constitutional Remedies (Article 32).",
                        "Article 21 guarantees that 'No person shall be deprived of his life or personal liberty except according to procedure established by law.' Through the Maneka Gandhi case (1978), the Supreme Court introduced 'due process of law' and expanded Article 21 to encompass the right to privacy (Puttaswamy case 2017), clean environment, and dignity."
                    ]),
                    ("3. Directive Principles of State Policy & Fundamental Duties", [
                        "Part IV (Articles 36 to 51) contains non-justiciable Directive Principles designed to establish a welfare state. Article 39(b) and (c) relate to the distribution of material resources and prevention of concentration of wealth.",
                        "Article 51A, inserted by the 42nd Amendment upon recommendation of the Swaran Singh Committee, lays down eleven Fundamental Duties for citizens."
                    ])
                ]
            ),
            (
                "parliamentary_governance.pdf",
                "UPSC Civil Services - Indian Polity & Governance",
                "Module 02: Union Legislature & Judicial Architecture",
                [
                    ("1. Parliament of India & Legislative Procedures", [
                        "The Parliament comprises the President, the Council of States (Rajya Sabha), and the House of the People (Lok Sabha). Rajya Sabha is a permanent body not subject to dissolution; one-third of its members retire every second year.",
                        "Money Bills (Article 110) can only be introduced in Lok Sabha upon prior recommendation of the President. The Rajya Sabha has only 14 days to return a Money Bill with recommendations, which Lok Sabha may accept or reject.",
                        "Joint sittings of both Houses (Article 108) are presided over by the Speaker of Lok Sabha. Joint sitting cannot be convened for Money Bills or Constitutional Amendment Bills."
                    ]),
                    ("2. Supreme Court & High Courts", [
                        "The Supreme Court of India is established under Article 124. It possesses Original Jurisdiction (Article 131), Appellate Jurisdiction (Articles 132-134), and Advisory Jurisdiction (Article 143).",
                        "Judicial review is a basic feature of the Constitution. The Collegium system for appointment of judges evolved through the First Judges (1981), Second Judges (1993), and Third Judges (1998) cases."
                    ])
                ]
            )
        ],
        "pyq": (
            "upsc_pyq_polity_2023_2024.pdf",
            "UPSC Previous Year Questions: Indian Polity (2023-2024)",
            "Official Pattern Reference with Answer Keys & Analysis",
            [
                ("Question 1 (UPSC CSE Prelims 2023)", [
                    "Q: In India, consider the following statements regarding the Attorney-General for India:",
                    "1. He is appointed by the President upon recommendation of the Union Cabinet.",
                    "2. He has the right of audience in all courts in the territory of India.",
                    "3. He has the right to take part in proceedings of both Houses of Parliament but without the right to vote.",
                    "Which of the statements given above are correct? (A) 1 and 2 only  (B) 2 and 3 only  (C) 1 and 3 only  (D) 1, 2 and 3",
                    "Answer: (D). Explanation: Under Article 76 and Article 88, the Attorney General possesses audience in all courts and can speak in Parliament without voting privileges."
                ]),
                ("Question 2 (UPSC CSE Prelims 2024)", [
                    "Q: Which of the following statements about Money Bills is NOT correct?",
                    "(A) A Money Bill cannot be introduced in the Rajya Sabha.",
                    "(B) If any question arises whether a Bill is a Money Bill or not, the decision of the Speaker is final.",
                    "(C) The President can return a Money Bill to the Parliament for reconsideration.",
                    "(D) The Rajya Sabha cannot amend or reject a Money Bill.",
                    "Answer: (C). Explanation: Under Article 111, the President cannot return a Money Bill for reconsideration because it is introduced with prior recommendation."
                ])
            ]
        )
    },
    "History": {
        "study": [
            (
                "ancient_medieval_india.pdf",
                "UPSC Civil Services - Indian History",
                "Module 01: Indus Valley, Mauryas, Guptas & Delhi Sultanate",
                [
                    ("1. Indus Valley Civilization & Vedic Age", [
                        "The Harappan civilization was an urban Bronze Age civilization known for grid-pattern town planning, burnt brick architecture, sophisticated drainage systems, and Great Granaries. Major sites include Mohenjo-daro, Harappa, Dholavira (water harvesting reservoirs), and Lothal (tidal dockyard).",
                        "The Early Vedic period was pastoral and egalitarian, where cattle represented wealth. The Later Vedic period witnessed territorial states (Janapadas), iron metallurgy (PGW culture), and rigidification of Varna distinctions."
                    ]),
                    ("2. Mauryan Empire & Ashokan Inscriptions", [
                        "Founded by Chandragupta Maurya with Chanakya's counsel. Ashoka embraced Buddhism after the Kalinga War (261 BCE) and propagated 'Dhamma' through rock and pillar edicts inscribed in Brahmi, Kharosthi, Aramaic, and Greek scripts.",
                        "The administrative apparatus described in Kautilya's Arthashastra featured centralized bureaucracy, spy networks (Gudhapurushas), and state revenue collectors (Samaharta)."
                    ]),
                    ("3. Delhi Sultanate & Vijayanagara Empire", [
                        "The Delhi Sultanate (1206-1526) established the Iqta administrative system. Alauddin Khalji introduced market control reforms, measurement of land (Zabita), and branding of horses (Dagh).",
                        "The Vijayanagara Empire (1336-1646), founded by Harihara and Bukka, reached its zenith under Krishnadeva Raya. Portuguese travellers Domingo Paes and Fernao Nuniz documented its prosperity and the Nayankara military tenure system."
                    ])
                ]
            ),
            (
                "modern_indian_history.pdf",
                "UPSC Civil Services - Indian History",
                "Module 02: British Expansion & The National Freedom Movement",
                [
                    ("1. Land Revenue Systems & Drain of Wealth", [
                        "British colonial policies instituted three distinct land revenue systems: Permanent Settlement (Cornwallis 1793 in Bengal/Bihar), Ryotwari System (Munro and Reed in Madras/Bombay), and Mahalwari System (Holt Mackenzie in Punjab and Central Provinces).",
                        "Dadabhai Naoroji formulated the 'Drain of Wealth' theory in 'Poverty and Un-British Rule in India', exposing economic exploitation through home charges, unrequited exports, and foreign capital repatriation."
                    ]),
                    ("2. Gandhian Mass Movements", [
                        "Non-Cooperation Movement (1920-22): Launched in response to the Rowlatt Act and Jallianwala Bagh massacre; suspended following the Chauri Chaura incident in February 1922.",
                        "Civil Disobedience Movement (1930): Commenced with the historic Dandi March from Sabarmati to coastal Dandi to break the salt law, symbolizing defiance against colonial state monopoly.",
                        "Quit India Movement (August 1942): Passed at Gowalia Tank Maidan with Gandhi's call 'Do or Die'. Led to underground networks organized by Aruna Asaf Ali, Jayaprakash Narayan, and Ram Manohar Lohia."
                    ])
                ]
            )
        ],
        "pyq": (
            "upsc_pyq_history_2023_2024.pdf",
            "UPSC Previous Year Questions: Indian History (2023-2024)",
            "Official Pattern Reference with Answer Keys & Analysis",
            [
                ("Question 1 (UPSC CSE Prelims 2023)", [
                    "Q: In the context of ancient Indian history, which of the following port cities was famous as a flourishing Roman trade center on the Coromandel coast?",
                    "(A) Arikamedu  (B) Tamralipti  (C) Muziris  (D) Sopara",
                    "Answer: (A). Explanation: Arikamedu (near Puducherry) was an active Indo-Roman trading port where amphorae jars, Roman glassware, and rouletted ware were excavated."
                ]),
                ("Question 2 (UPSC CSE Prelims 2024)", [
                    "Q: Consider the following events during the freedom struggle: 1. Cabinet Mission 2. Cripps Mission 3. Wavell Plan 4. Quit India Movement. What is the correct chronological sequence?",
                    "(A) 2 - 4 - 3 - 1  (B) 4 - 2 - 1 - 3  (C) 2 - 3 - 4 - 1  (D) 3 - 2 - 4 - 1",
                    "Answer: (A). Explanation: Cripps Mission (March 1942), Quit India (August 1942), Wavell Plan (June 1945), Cabinet Mission (March 1946)."
                ])
            ]
        )
    },
    "Geography": {
        "study": [
            (
                "physical_geography.pdf",
                "UPSC Civil Services - Geography",
                "Module 01: Geomorphology, Climatology & Oceanography",
                [
                    ("1. Plate Tectonics & Continental Drift", [
                        "Alfred Wegener proposed the Continental Drift theory in 1912, positing supercontinent Pangea and Panthalassa. Modern Plate Tectonic theory establishes that the lithosphere is divided into major and minor tectonic plates floating on the asthenosphere.",
                        "Plate boundaries are divergent (mid-ocean ridges), convergent (subduction zones and fold mountains like the Himalayas), and transform (San Andreas fault). Earthquakes and volcanic arcs predominantly concentrate along the Pacific 'Ring of Fire'."
                    ]),
                    ("2. Atmospheric Circulation & Monsoon Dynamics", [
                        "Global atmospheric cells include Hadley, Ferrel, and Polar cells, driving planetary trade winds, westerlies, and polar easterlies. The Intertropical Convergence Zone (ITCZ) shifts seasonally with solar declination.",
                        "The Indian Southwest Monsoon is governed by the thermal contrast between the Tibetan Plateau and the Indian Ocean, the Tropical Easterly Jet (TEJ), Somali Jet, El Niño-Southern Oscillation (ENSO), and the Indian Ocean Dipole (IOD)."
                    ])
                ]
            ),
            (
                "indian_geography_resources.pdf",
                "UPSC Civil Services - Geography",
                "Module 02: Drainage Systems, Soils & Mineral Resources of India",
                [
                    ("1. Himalayan vs Peninsular River Systems", [
                        "Himalayan rivers (Indus, Ganga, Brahmaputra) are antecedent, perennial, fed by glacial melt, and form deep gorges, meandering loops, and vast deltas (Sundarbans).",
                        "Peninsular rivers (Godavari, Krishna, Cauvery, Mahanadi, Narmada, Tapti) are superimposed, seasonal, flow through graded rift valleys (Narmada and Tapti flow westward into the Arabian Sea without forming deltas).",
                        "Godavari (Dakshin Ganga) is the longest peninsular river, originating from Trimbakeshwar in the Western Ghats."
                    ]),
                    ("2. Soil Classification & Agricultural Regions", [
                        "Alluvial soils cover over 40% of India's landmass in Indo-Gangetic plains, subdivided into Khadar (newer alluvium) and Bhangar (older calcareous alluvium).",
                        "Black soils (Regur) developed on basaltic Deccan lava trap, highly argillaceous with high moisture retention, ideally suited for cotton cultivation."
                    ])
                ]
            )
        ],
        "pyq": (
            "upsc_pyq_geography_2023_2024.pdf",
            "UPSC Previous Year Questions: Geography (2023-2024)",
            "Official Pattern Reference with Answer Keys & Analysis",
            [
                ("Question 1 (UPSC CSE Prelims 2023)", [
                    "Q: Consider the following rivers: 1. Jhelum 2. Chenab 3. Ravi 4. Sutlej. Which one of the following joins the Indus directly?",
                    "(A) Jhelum  (B) Chenab  (C) Ravi  (D) Sutlej (via Panjnad)",
                    "Answer: (D / Panjnad confluence context). Explanation: All Punjab rivers coalesce into Panjnad before emptying into the Indus near Mithankot."
                ]),
                ("Question 2 (UPSC CSE Prelims 2024)", [
                    "Q: With reference to Indian Ocean Dipole (IOD), consider the following statements:",
                    "1. Positive IOD leads to warmer waters in western Indian Ocean and results in surplus rainfall in the Indian subcontinent.",
                    "2. A positive IOD phenomenon can counteract the adverse impact of El Niño.",
                    "Which of the statements given above is/are correct? (A) 1 only  (B) 2 only  (C) Both 1 and 2  (D) Neither 1 nor 2",
                    "Answer: (C). Both statements are correct."
                ])
            ]
        )
    },
    "Economy": {
        "study": [
            (
                "macroeconomics_fiscal_policy.pdf",
                "UPSC Civil Services - Indian Economy",
                "Module 01: National Income, Inflation & Fiscal Architecture",
                [
                    ("1. GDP Measurement & National Accounting", [
                        "Gross Domestic Product (GDP) represents the monetary value of final goods and services produced within economic borders over a period. Real GDP adjusts nominal GDP for inflation using the GDP Deflator.",
                        "Gross National Product (GNP) equals GDP plus Net Factor Income from Abroad (NFIA). Net Domestic Product (NDP) accounts for capital depreciation."
                    ]),
                    ("2. Fiscal Deficit & FRBM Framework", [
                        "Fiscal Deficit is the excess of total budget expenditure over non-debt creating receipts (Revenue receipts + Recovery of loans + Disinvestment). It indicates total government borrowing requirements.",
                        "The Fiscal Responsibility and Budget Management (FRBM) Act targets prudent debt-to-GDP ratios and containment of fiscal deficit to sustainable limits."
                    ])
                ]
            ),
            (
                "banking_monetary_policy.pdf",
                "UPSC Civil Services - Indian Economy",
                "Module 02: Reserve Bank of India & Monetary Management",
                [
                    ("1. Monetary Policy Committee (MPC) & Policy Tools", [
                        "The six-member Monetary Policy Committee (3 RBI representatives, 3 government nominees) is statutory under the RBI Act, 1934. It targets consumer price index (CPI) headline inflation of 4% with a tolerance band of +/- 2%.",
                        "Key quantitative instruments include Repo Rate (rate at which RBI lends short-term funds against government securities), Standing Deposit Facility (SDF - non-collateralized liquidity absorption), and Cash Reserve Ratio (CRR)."
                    ]),
                    ("2. Non-Performing Assets (NPAs) & IBC 2016", [
                        "Loans overdue past 90 days are categorized as Gross NPAs. The Insolvency and Bankruptcy Code (IBC) 2016 provides time-bound corporate insolvency resolution processes (CIRP) via National Company Law Tribunal (NCLT)."
                    ])
                ]
            )
        ],
        "pyq": (
            "upsc_pyq_economy_2023_2024.pdf",
            "UPSC Previous Year Questions: Indian Economy (2023-2024)",
            "Official Pattern Reference with Answer Keys & Analysis",
            [
                ("Question 1 (UPSC CSE Prelims 2023)", [
                    "Q: In India, which one of the following is responsible for maintaining price stability by controlling inflation?",
                    "(A) Department of Consumer Affairs  (B) Ministry of Finance  (C) Reserve Bank of India  (D) NITI Aayog",
                    "Answer: (C). Explanation: Under the RBI Act 1934 amended in 2016, the Reserve Bank of India is legally tasked with inflation targeting."
                ]),
                ("Question 2 (UPSC CSE Prelims 2024)", [
                    "Q: Consider the following actions by the Reserve Bank of India: 1. Raising the Repo Rate 2. Selling government securities in open market 3. Lowering the Cash Reserve Ratio. Which of these help in curtailing money supply? (A) 1 and 2 only  (B) 2 and 3 only  (C) 1 and 3 only  (D) 1, 2 and 3",
                    "Answer: (A). Explanation: Raising repo rate and open market sales absorb liquidity, whereas lowering CRR increases money supply."
                ])
            ]
        )
    },
    "Environment": {
        "study": [
            (
                "biodiversity_conservation.pdf",
                "UPSC Civil Services - Environment & Ecology",
                "Module 01: Biodiversity, National Parks & Wildlife Protection",
                [
                    ("1. Ecosystem Trophic Levels & Biodiversity Hotspots", [
                        "Ecosystem structure depends on trophic energy transfer adhering to Lindeman's 10% rule. Keystone species exert disproportionate influence on ecological community integrity (e.g., tigers, sea otters).",
                        "Norman Myers defined Biodiversity Hotspots by two strict criteria: containing at least 1,500 endemic vascular plant species, and having lost at least 70% of primary original habitat. India hosts four hotspots: Western Ghats, Himalayas, Indo-Burma, and Sundaland."
                    ]),
                    ("2. Wildlife Protection Act (1972) & Protected Areas", [
                        "The Wildlife Protection Act 1972 establishes Protected Areas: National Parks (highest protection, no human settlement or grazing allowed), Wildlife Sanctuaries, and Conservation/Community Reserves.",
                        "Project Tiger (1973) operates under the National Tiger Conservation Authority (NTCA). Biosphere Reserves integrate core, buffer, and transition zones under UNESCO's Man and the Biosphere (MAB) program."
                    ])
                ]
            ),
            (
                "climate_change_treaties.pdf",
                "UPSC Civil Services - Environment & Ecology",
                "Module 02: Climate Change Treaties & Global Environmental Conventions",
                [
                    ("1. UNFCCC, Kyoto Protocol & Paris Agreement", [
                        "The 1992 Rio Earth Summit gave rise to three Rio Conventions: UNFCCC, CBD, and UNCCD. The 1997 Kyoto Protocol established binding emission cuts for Annex I countries using carbon trading and Clean Development Mechanism (CDM).",
                        "The 2015 Paris Agreement established Nationally Determined Contributions (NDCs) aimed at restricting global average temperature rise well below 2°C, and striving for 1.5°C above pre-industrial baselines."
                    ]),
                    ("2. Ramsar Convention & Ozone Depletion", [
                        "The Ramsar Convention on Wetlands (1971) promotes conservation of wetlands of international importance. The Montreux Record highlights wetlands facing technological or human threats.",
                        "The Montreal Protocol (1987) with Kigali Amendment (2016) mandates phased phase-down of Hydrofluorocarbons (HFCs) alongside Chlorofluorocarbons (CFCs)."
                    ])
                ]
            )
        ],
        "pyq": (
            "upsc_pyq_environment_2023_2024.pdf",
            "UPSC Previous Year Questions: Environment & Ecology (2023-2024)",
            "Official Pattern Reference with Answer Keys & Analysis",
            [
                ("Question 1 (UPSC CSE Prelims 2023)", [
                    "Q: Consider the following fauna: 1. Lion-tailed Macaque 2. Malabar Civet 3. Sambar Deer. Which of the above are naturally found in the Western Ghats? (A) 1 and 2 only  (B) 2 and 3 only  (C) 1 and 3 only  (D) 1, 2 and 3",
                    "Answer: (D). All three are found in the Western Ghats ecosystem."
                ]),
                ("Question 2 (UPSC CSE Prelims 2024)", [
                    "Q: Which of the following statements about Ramsar Convention Montreux Record is correct?",
                    "(A) It is a register of wetland sites where ecological changes have occurred, are occurring, or are likely to occur.",
                    "(B) It is a database for measuring carbon sequestration in mangroves.",
                    "(C) It is a list of extinct marine organisms.",
                    "(D) It grants legal patents to tribal forest dwellers.",
                    "Answer: (A). Keoladeo National Park and Loktak Lake are listed on India's Montreux Record."
                ])
            ]
        )
    },
    "Science_and_Technology": {
        "study": [
            (
                "biotechnology_space_tech.pdf",
                "UPSC Civil Services - Science & Technology",
                "Module 01: Biotechnology, Gene Editing & Space Exploration",
                [
                    ("1. Recombinant DNA & CRISPR-Cas9 Technology", [
                        "CRISPR-Cas9 operates as molecular scissors utilizing a guide RNA (gRNA) complementary to target DNA sequences and the Cas9 endonuclease to introduce precise double-stranded breaks.",
                        "Applications include therapeutic correction of genetic sickle cell anemia, thalassemia, disease-resistant GM crops (Bt cotton with cry1Ac gene), and mRNA vaccines targeting viral spike proteins."
                    ]),
                    ("2. ISRO Missions & Space Trajectories", [
                        "ISRO's launch vehicles comprise PSLV (Polar Satellite Launch Vehicle - workhorse for Sun-synchronous polar orbits) and LVM3 (Geosynchronous Launch Vehicle Mark III for cryogenic heavy payloads).",
                        "Milestone interplanetary missions include Chandrayaan-3 (demonstrating soft landing on lunar south polar region with Vikram lander and Pragyan rover) and Aditya-L1 (stationed at Sun-Earth Lagrange Point 1 to study the solar corona)."
                    ])
                ]
            ),
            (
                "emerging_technologies_ai_quantum.pdf",
                "UPSC Civil Services - Science & Technology",
                "Module 02: Quantum Computing, Artificial Intelligence & Nanomaterials",
                [
                    ("1. Quantum Mechanics & Superposition in Computing", [
                        "Classical computing relies on binary bits (0 or 1). Quantum computers exploit quantum superposition and entanglement in qubits, enabling exponential speedups in factoring and molecular simulation.",
                        "India's National Quantum Mission focuses on developing quantum communication, quantum cryptography (QKD), and quantum sensing."
                    ]),
                    ("2. 5G/6G Networks & Graphene Nanomaterials", [
                        "5G telecommunications utilize millimeter-wave frequencies, massive MIMO (Multiple Input Multiple Output), and beamforming to achieve gigabit speeds with low latency.",
                        "Graphene is a single-atom-thick layer of carbon arranged in a 2D hexagonal honeycomb lattice, possessing extraordinary electrical conductivity, mechanical tensile strength, and optical transparency."
                    ])
                ]
            )
        ],
        "pyq": (
            "upsc_pyq_scitech_2023_2024.pdf",
            "UPSC Previous Year Questions: Science & Technology (2023-2024)",
            "Official Pattern Reference with Answer Keys & Analysis",
            [
                ("Question 1 (UPSC CSE Prelims 2023)", [
                    "Q: What is the primary operational objective of the James Webb Space Telescope (JWST)?",
                    "(A) To detect seismic activity on Mars",
                    "(B) To study infrared emissions from the earliest galaxies formed after the Big Bang",
                    "(C) To generate solar flare forecasts for commercial aviation",
                    "(D) To measure ocean salinity on Earth",
                    "Answer: (B). JWST operates in infrared bands at Lagrange Point 2."
                ]),
                ("Question 2 (UPSC CSE Prelims 2024)", [
                    "Q: With reference to mRNA vaccines, consider the following statements:",
                    "1. They deliver instructions to human cells to produce a harmless viral spike protein.",
                    "2. They permanently alter the recipient's nuclear genomic DNA.",
                    "Which of the statements given above is/are correct? (A) 1 only  (B) 2 only  (C) Both 1 and 2  (D) Neither 1 nor 2",
                    "Answer: (A). mRNA degrades in the cytoplasm and never enters the cell nucleus."
                ])
            ]
        )
    },
    "Art_and_Culture": {
        "study": [
            (
                "temple_architecture_sculpture.pdf",
                "UPSC Civil Services - Indian Art & Culture",
                "Module 01: Classical Architecture, Caves & Sculpture",
                [
                    ("1. Nagara, Dravida & Vesara Temple Styles", [
                        "Nagara style (North India): Characterized by curvilinear shikhara (latina or phamsana), absence of boundary walls or gopurams, elevated plinths (jagati), and amalaka-kalasha finial. Examples: Sun Temple Konark, Khajuraho temples.",
                        "Dravida style (South India): Characterized by enclosed compound walls, monumental entrance gateways (Gopuram), pyramidal tiered tower (Vimana), pillared halls (Mandapa), and temple water tank (Kalyani). Examples: Brihadeeswarar Temple Tanjore.",
                        "Vesara style: Hybrid style synthesized by Chalukyas of Badami and Hoysalas at Belur and Halebidu with star-shaped (stellate) ground plans."
                    ]),
                    ("2. Rock-Cut Architecture of Ajanta & Ellora", [
                        "Ajanta Caves (29 rock-cut Buddhist caves) in Maharashtra, renowned for Mural Fresco paintings depicting Jataka tales, Bodhisattva Padmapani and Vajrapani.",
                        "Ellora Caves (34 caves representing Buddhism, Brahmanism, and Jainism). Cave 16 houses the monolithic rock-cut Kailashnath Temple carved top-down under Rashtrakuta King Krishna I."
                    ])
                ]
            ),
            (
                "classical_dances_music_paintings.pdf",
                "UPSC Civil Services - Indian Art & Culture",
                "Module 02: Classical Dances, Music & Miniature Traditions",
                [
                    ("1. Classical Dance Forms of India", [
                        "Sangeet Natak Akademi recognizes 8 classical dance traditions rooted in Bharata Muni's Natya Shastra: Bharatanatyam (Tamil Nadu - ekaharya solo), Kathakali (Kerala - elaborate facial makeup & mudras), Kathak (North India - footwork & chakkars), Odissi (Odisha - tribhanga posture), Kuchipudi (Andhra Pradesh - tarangam brass plate balance), Manipuri (Manipur - Rasleela devotion), Mohiniyattam (Kerala - lasya grace), and Sattriya (Assam - Bhakti tradition of Srimanta Sankardev)."
                    ]),
                    ("2. Miniature Painting Schools", [
                        "Mughal miniature school synthesized Persian delicacy with indigenous Indian naturalism (Tutinama, Hamzanama).",
                        "Rajasthani schools include Mewar (bold pigments), Bundi (nature and water bodies), and Kishangarh (famed for Bani Thani painted by Nihal Chand)."
                    ])
                ]
            )
        ],
        "pyq": (
            "upsc_pyq_artculture_2023_2024.pdf",
            "UPSC Previous Year Questions: Indian Art & Culture (2023-2024)",
            "Official Pattern Reference with Answer Keys & Analysis",
            [
                ("Question 1 (UPSC CSE Prelims 2023)", [
                    "Q: With reference to ancient Indian rock-cut architecture, which one of the following is the finest example of a monolithic temple carved out of a single rock from top to bottom?",
                    "(A) Shore Temple, Mahabalipuram  (B) Kailash Temple, Ellora  (C) Brihadisvara Temple, Thanjavur  (D) Sun Temple, Modhera",
                    "Answer: (B). The Kailashnath Temple (Cave 16) at Ellora."
                ]),
                ("Question 2 (UPSC CSE Prelims 2024)", [
                    "Q: Consider the following pairs of classical dance and associated elements: 1. Sattriya - Srimanta Sankardev 2. Kuchipudi - Tarangam brass plate dance 3. Odissi - Tribhanga posture. How many of the pairs given above are correctly matched? (A) Only one pair  (B) Only two pairs  (C) All three pairs  (D) None",
                    "Answer: (C). All three pairs are correctly matched."
                ])
            ]
        )
    },
    "Ethics": {
        "study": [
            (
                "ethics_human_interface_values.pdf",
                "UPSC Civil Services - Ethics, Integrity & Aptitude",
                "Module 01: Ethics and Human Interface, Moral Thinkers & Values",
                [
                    ("1. Essence, Determinants & Consequences of Ethics", [
                        "Ethics defines systematic standards of right and wrong governing human actions. Key determinants include social institutions, legal systems, cultural norms, and individual conscience.",
                        "Consequentialist ethics (Utilitarianism by Jeremy Bentham and J.S. Mill) evaluates moral worth by the greatest happiness for the greatest number. Deontological ethics (Immanuel Kant) posits categorical imperatives where duties are intrinsically moral regardless of outcome."
                    ]),
                    ("2. Emotional Intelligence in Administration", [
                        "Daniel Goleman's model identifies five domains: Self-awareness, Self-regulation, Motivation, Empathy, and Social skills. Empathy and emotional composure enable civil servants to resolve public conflicts, manage administrative stress, and deliver compassionate governance."
                    ])
                ]
            ),
            (
                "probity_in_governance_case_studies.pdf",
                "UPSC Civil Services - Ethics, Integrity & Aptitude",
                "Module 02: Probity in Governance, Nolan Principles & Accountability",
                [
                    ("1. Nolan Committee Principles of Public Life", [
                        "The Seven Principles of Public Life are: 1. Selflessness 2. Integrity 3. Objectivity 4. Accountability 5. Openness 6. Honesty 7. Leadership. These form the benchmark for ethical civil service conduct globally.",
                        "Conflict of Interest arises when public duties conflict with personal, familial, or financial interests; public officials must recuse themselves and maintain transparent disclosure."
                    ]),
                    ("2. Whistleblowing & Citizen's Charters", [
                        "Whistleblower Protection Act protects individuals exposing corruption or misuse of power in public administration. Citizen's Charters commit organizations to transparent standards, timeframes, and grievance redressal mechanisms."
                    ])
                ]
            )
        ],
        "pyq": (
            "upsc_pyq_ethics_2023_2024.pdf",
            "UPSC Previous Year Questions: Ethics & Aptitude (2023-2024)",
            "Official Pattern Reference with Answer Keys & Analysis",
            [
                ("Question 1 (UPSC CSE Prelims / Ethics Test)", [
                    "Q: Which of the following is NOT one of the Seven Nolan Principles of Public Life?",
                    "(A) Selflessness  (B) Integrity  (C) Profitability  (D) Objectivity",
                    "Answer: (C). The Seven Nolan Principles are Selflessness, Integrity, Objectivity, Accountability, Openness, Honesty, and Leadership."
                ]),
                ("Question 2 (UPSC CSE Prelims / Ethics Test)", [
                    "Q: What distinguishes Deontology from Utilitarianism in moral philosophy?",
                    "(A) Deontology prioritizes duty and moral rules regardless of consequence, whereas Utilitarianism judges an action by its net outcome.",
                    "(B) Utilitarianism considers only financial profit.",
                    "(C) Deontology denies the existence of moral laws.",
                    "(D) There is no conceptual distinction between them.",
                    "Answer: (A). Kantian deontology focuses on duty and universal moral law."
                ])
            ]
        )
    }
}

def generate_all():
    print(f"Generating UPSC PDFs in {BASE_UPSC_DIR}...")
    for subj_name, data in SUBJECT_DATA.items():
        study_dir = BASE_UPSC_DIR / subj_name / "study_material"
        pyq_dir = BASE_UPSC_DIR / subj_name / "previous_year_questions"
        
        # 1. Study materials
        for filename, title, subtitle, sections in data["study"]:
            create_pdf(study_dir / filename, title, subtitle, sections)
            
        # 2. PYQ
        pyq_filename, pyq_title, pyq_sub, pyq_sections = data["pyq"]
        create_pdf(pyq_dir / pyq_filename, pyq_title, pyq_sub, pyq_sections)
        
    print("All 24 dummy UPSC PDFs generated successfully.")

if __name__ == "__main__":
    generate_all()
