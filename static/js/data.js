// Sample Bidding Data for Cleveland, Ohio Area
const opportunities = [
    {
        id: 1,
        title: "Storm Sewer Cleaning and CCTV Inspection Services - Annual Contract",
        description: "Annual contract for storm sewer cleaning, vac truck services, and CCTV inspection of municipal drainage systems. Services include hydro-jetting, vacuum excavation, and video inspection with detailed reporting.",
        location: "Cleveland, OH",
        type: "municipal",
        source: "City of Cleveland",
        bidNumber: "CLV-2026-0045",
        postedDate: "2026-01-20",
        deadline: "2026-02-15",
        url: "https://www.clevelandohio.gov/city-hall/departments/city-finance/purchasing-department",
        tags: ["stormwater", "vac-truck", "cleaning", "cctv"],
        daysUntilDeadline: 19
    },
    {
        id: 2,
        title: "Catch Basin Cleaning and Maintenance Services",
        description: "Countywide catch basin cleaning, storm drain maintenance, and vacuum truck services for stormwater infrastructure. Includes emergency response capabilities and regular scheduled maintenance.",
        location: "Cuyahoga County, OH",
        type: "county",
        source: "Cuyahoga County",
        bidNumber: "CC-PW-2026-012",
        postedDate: "2026-01-18",
        deadline: "2026-02-10",
        url: "https://cuyahogacounty.us/business/procurement",
        tags: ["stormwater", "vac-truck", "cleaning"],
        daysUntilDeadline: 14
    },
    {
        id: 3,
        title: "Stormwater Compliance and Drainage System Maintenance",
        description: "ODOT stormwater compliance services including drainage cleaning, vac truck operations, and regulatory reporting for Region 3 (Northeast Ohio). Must meet all EPA and state environmental standards.",
        location: "Region 3 (Northeast Ohio)",
        type: "state",
        source: "State of Ohio - ODOT",
        bidNumber: "ODOT-SW-2026-089",
        postedDate: "2026-01-15",
        deadline: "2026-02-28",
        url: "https://procure.ohio.gov/",
        tags: ["stormwater", "vac-truck", "compliance"],
        daysUntilDeadline: 32
    },
    {
        id: 4,
        title: "Sanitary Sewer Jet Cleaning and Hydro Excavation Services",
        description: "Emergency and scheduled sewer cleaning using hydro-jetting and vacuum excavation equipment. 24/7 emergency response required. Must have experience with municipal infrastructure and safety protocols.",
        location: "Cleveland, OH",
        type: "municipal",
        source: "City of Cleveland - Water Department",
        bidNumber: "CLV-WTR-2026-0078",
        postedDate: "2026-01-22",
        deadline: "2026-02-20",
        url: "https://www.clevelandohio.gov/city-hall/departments/city-finance/purchasing-department",
        tags: ["sewer", "vac-truck", "cleaning", "emergency"],
        daysUntilDeadline: 24
    },
    {
        id: 5,
        title: "Street Sweeping and Storm Drain Cleaning - Zone 2",
        description: "Combined street sweeping and storm drain cleaning services for eastern county municipalities. Includes routine maintenance and pre-storm preparation. Multi-year contract opportunity.",
        location: "Cuyahoga County, OH",
        type: "county",
        source: "Cuyahoga County - Public Works",
        bidNumber: "CC-ENG-2026-003",
        postedDate: "2026-01-10",
        deadline: "2026-02-05",
        url: "https://cuyahogacounty.us/business/procurement",
        tags: ["cleaning", "stormwater", "sweeping"],
        daysUntilDeadline: 9
    }
];

// Export for use in app.js
window.bidOpportunities = opportunities;
