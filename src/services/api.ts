// Streamlined Data Layer for PS07 India Geospatial AI Pattern Recognition & Hazard Intelligence
// v2 - forcing rebuild
export interface SocialGatheringHotspot {
  id: string;
  name: string;
  category: 'Bazar / Open Market' | 'Shopping Mall / Commercial Hub' | 'Public Park / Gathering Ground' | 'Transit Hub / Railway Station';
  distanceKm: number;
  coordinates: [number, number];
  peakCrowdEstimate: string;
  riskPriority: 'CRITICAL HIGH-DENSITY ALERT' | 'URGENT EVACUATION WARNING';
  evacuationDirective: string;
}

export interface HazardZone {
  id: string;
  name: string;
  isLive?: boolean;
  targetTownVillage: string;
  subDistrictDistrict: string;
  stateRegion: string;
  disasterType: 'Flash Flood' | 'Landslide' | 'Cyclone Surge' | 'Wildfire' | 'Micro-Seismic';
  riskLevel: 'Low' | 'Medium' | 'High';
  confidencePercentage: number;
  coordinates: [number, number];
  epicenterFocalPoint: string;
  historicalPatternMatch: string;
  primaryAnomalyDriver: string;
  satelliteRadarSig: string;
  weatherCorrelation: string;
  topographyFactor: string;
  citizenAlertStatus: 'Active Alert Issued' | 'Ready to Dispatch' | 'Monitoring Only';
  affectedPopulationEstimate: string;
  xaiReasoning: string;
  socialGatheringHotspots: SocialGatheringHotspot[];
}

export function formatCoordinates(coords: [number, number]): string {
  const lat = coords[0];
  const lng = coords[1];
  const latStr = `${Math.abs(lat).toFixed(4)}° ${lat >= 0 ? 'N' : 'S'}`;
  const lngStr = `${Math.abs(lng).toFixed(4)}° ${lng >= 0 ? 'E' : 'W'}`;
  return `${latStr}, ${lngStr}`;
}

export interface UserLocationHazardAssessment {
  userLat: number;
  userLng: number;
  locationName: string;
  nearestHazard: HazardZone;
  distanceKm: number;
  isDangerDetected: boolean;
}

export const INDIA_HAZARD_ZONES: HazardZone[] = [
  // {
  //   id: 'HAZ-IND-01',
  //   name: 'Kurla-Mithi River Floodplain Sector',
  //   targetTownVillage: 'Bail Bazar & Kranti Nagar Ward (Kurla West)',
  //   subDistrictDistrict: 'Kurla Taluka, Mumbai Suburban District',
  //   stateRegion: 'Maharashtra',
  //   disasterType: 'Flash Flood',
  //   riskLevel: 'High',
  //   confidencePercentage: 94,
  //   coordinates: [19.0825, 72.8856],
  //   epicenterFocalPoint: 'Mithi River Bottleneck & Kranti Nagar Lowland Settlement',
  //   historicalPatternMatch: '96.2% match with July 2005 Mithi River Overflow Baseline',
  //   primaryAnomalyDriver: 'Sentinel-2 SAR Dielectric Water Backscatter Drop >85%',
  //   satelliteRadarSig: 'High SAR backscatter drop indicating 14.2 sqkm water inundation',
  //   weatherCorrelation: 'OpenWeather Radar: 92mm/hr sustained monsoon intensity',
  //   topographyFactor: 'OSM Low-elevation river embankment runoff obstruction',
  //   citizenAlertStatus: 'Active Alert Issued',
  //   affectedPopulationEstimate: '34,500 Local Ward Residents',
  //   xaiReasoning: 'Unanimous multi-spectral agreement across Sentinel-2 SAR radar drop and OpenWeather precipitation rates. Historical spatial correlation matches 2005 inundation baseline with >94% confidence.',
  //   socialGatheringHotspots: [
  //     {
  //       id: 'HOT-01-A',
  //       name: 'Bail Bazar Wholesale Fruit & Spice Market',
  //       category: 'Bazar / Open Market',
  //       distanceKm: 0.2,
  //       coordinates: [19.0831, 72.8862],
  //       peakCrowdEstimate: '16,500 Shoppers & Vendors',
  //       riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
  //       evacuationDirective: 'Broadcast emergency siren via Market Committee PA & evacuate ground vendors to elevated concrete plaza.',
  //     },
  //     {
  //       id: 'HOT-01-B',
  //       name: 'Phoenix Marketcity Commercial Complex',
  //       category: 'Shopping Mall / Commercial Hub',
  //       distanceKm: 0.8,
  //       coordinates: [19.0864, 72.8890],
  //       peakCrowdEstimate: '22,000 Visitors',
  //       riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
  //       evacuationDirective: 'Trigger Mall Management PA System to direct lower basement parking visitors to upper floor exits.',
  //     },
  //   ],
  // },
  {
    id: 'HAZ-IND-02',
    name: 'Malana Parvati-Valley Slope Belt',
    targetTownVillage: 'Malana Village & Jari Transit Corridor',
    subDistrictDistrict: 'Bhuntar Sub-Division, Kullu District',
    stateRegion: 'Himachal Pradesh',
    disasterType: 'Landslide',
    riskLevel: 'High',
    confidencePercentage: 88,
    coordinates: [32.0628, 77.2619],
    epicenterFocalPoint: 'Parvati River Canyon Steep Slope Slip Focal Point',
    historicalPatternMatch: '89.4% match with August 2023 Monsoon Slope Slip',
    primaryAnomalyDriver: 'InSAR Satellite Terrain Displacement >12mm in 24h',
    satelliteRadarSig: 'Interferometric SAR radar detects high shear slope instability',
    weatherCorrelation: 'Continuous 145mm precipitation over saturated terrain',
    topographyFactor: 'Steep slope gradient >38° in populated transit corridor',
    citizenAlertStatus: 'Ready to Dispatch',
    affectedPopulationEstimate: '14,200 Mountain Village Residents',
    xaiReasoning: 'Interferometric synthetic aperture radar (InSAR) confirms active soil movement exceeding critical stability thresholds. Saturated soil weight combined with high slope angle indicates imminent slope failure.',
    socialGatheringHotspots: [
      {
        id: 'HOT-02-A',
        name: 'Malana Central Village Market Square',
        category: 'Bazar / Open Market',
        distanceKm: 0.1,
        coordinates: [32.0632, 77.2624],
        peakCrowdEstimate: '3,800 Villagers & Traders',
        riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
        evacuationDirective: 'Alert Village Panchayat council to sound village bell & move traders away from cliffside stalls.',
      },
      {
        id: 'HOT-02-B',
        name: 'Jari Valley Taxi Stand & Transit Hub',
        category: 'Transit Hub / Railway Station',
        distanceKm: 1.4,
        coordinates: [32.0489, 77.2435],
        peakCrowdEstimate: '1,500 Commuters & Tourists',
        riskPriority: 'URGENT EVACUATION WARNING',
        evacuationDirective: 'Halt upstream vehicle dispatch & guide tourist taxis to valley safe staging area.',
      },
    ],
  },
  // {
  //   id: 'HAZ-IND-03',
  //   name: 'Dhamra Estuary Coastal Sector',
  //   targetTownVillage: 'Kasia Coastal Village & Dhamra Township',
  //   subDistrictDistrict: 'Chandbali Block, Bhadrak District',
  //   stateRegion: 'Odisha',
  //   disasterType: 'Cyclone Surge',
  //   riskLevel: 'Medium',
  //   confidencePercentage: 62,
  //   coordinates: [20.7963, 86.8906],
  //   epicenterFocalPoint: 'Mangrove Delta Sea Surge Embankment Breach Point',
  //   historicalPatternMatch: '64.0% match with Cyclone Fani 2019 Outer Rainbands',
  //   primaryAnomalyDriver: 'Sea Surface Temperature anomaly + Barometric Pressure Drop',
  //   satelliteRadarSig: 'MODIS Ocean Thermal Imaging shows +2.1°C SST elevation',
  //   weatherCorrelation: 'Wind shear vectors velocity 65 km/h with 4.2m wave swell',
  //   topographyFactor: 'Flat low-lying coastal alluvial plain vulnerable to surge',
  //   citizenAlertStatus: 'Monitoring Only',
  //   affectedPopulationEstimate: '18,500 Coastal Estate Residents',
  //   xaiReasoning: 'Thermal imaging and barometric pressure drops align with early-stage cyclonic vortex formation. Confidence is rated at 62% due to variable offshore wind trajectory predictions.',
  //   socialGatheringHotspots: [
  //     {
  //       id: 'HOT-03-A',
  //       name: 'Dhamra Fishing Harbor & Daily Fish Bazar',
  //       category: 'Bazar / Open Market',
  //       distanceKm: 0.5,
  //       coordinates: [20.7981, 86.8925],
  //       peakCrowdEstimate: '6,500 Fishermen & Buyers',
  //       riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
  //       evacuationDirective: 'Broadcast Port Authority siren & recall all fishing trawlers to storm harbor.',
  //     },
  //     {
  //       id: 'HOT-03-B',
  //       name: 'Chandbali Township Central Market',
  //       category: 'Shopping Mall / Commercial Hub',
  //       distanceKm: 1.8,
  //       coordinates: [20.7810, 86.7450],
  //       peakCrowdEstimate: '8,200 Traders',
  //       riskPriority: 'URGENT EVACUATION WARNING',
  //       evacuationDirective: 'Issue commercial market warning & open cyclone shelter gates.',
  //     },
  //   ],
  // },
  {
    id: 'HAZ-IND-04',
    name: 'Chooralmala-Mundakkai Slope Ridge',
    targetTownVillage: 'Chooralmala Town & Punchirimattam Slope',
    subDistrictDistrict: 'Meppadi Panchayat, Wayanad District',
    stateRegion: 'Kerala',
    disasterType: 'Landslide',
    riskLevel: 'Medium',
    confidencePercentage: 54,
    coordinates: [11.5214, 76.1583],
    epicenterFocalPoint: 'Iruvaipuzha River Basin Debris Flow Bottleneck',
    historicalPatternMatch: '52.8% match with July 2024 Debris Flow Cluster',
    primaryAnomalyDriver: 'Discrepancy: Rainfall threshold breached but zero ground shift on radar',
    satelliteRadarSig: 'InSAR satellite shows zero physical deformation (<0.4mm)',
    weatherCorrelation: 'High rainfall 110mm in 6h exceeds threshold by 30%',
    topographyFactor: 'Debris flow channel with historical slip scars',
    citizenAlertStatus: 'Monitoring Only',
    affectedPopulationEstimate: '12,800 Plantation Village Residents',
    xaiReasoning: 'DISCREPANCY DETECTED: While weather radar indicates extreme rainfall, spaceborne InSAR radar confirms zero ground movement over the past 12 hours. Lower confidence (54%) assigned pending field drone verification.',
    socialGatheringHotspots: [
      {
        id: 'HOT-04-A',
        name: 'Chooralmala Central Town Bazar & Bus Stand',
        category: 'Bazar / Open Market',
        distanceKm: 0.2,
        coordinates: [11.5220, 76.1590],
        peakCrowdEstimate: '4,500 Local Villagers',
        riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
        evacuationDirective: 'Transmit urgent SMS to Panchayath ward members & clear bridge bazaar area.',
      },
      {
        id: 'HOT-04-B',
        name: 'Punchirimattam Tea Estate Worker Settlement',
        category: 'Public Park / Gathering Ground',
        distanceKm: 1.1,
        coordinates: [11.5260, 76.1620],
        peakCrowdEstimate: '2,100 Estate Workers',
        riskPriority: 'URGENT EVACUATION WARNING',
        evacuationDirective: 'Deploy local siren vehicles to guide plantation workers to hill refuge.',
      },
    ],
  },
  // {
  //   id: 'HAZ-IND-05',
  //   name: 'Sangamner Pravara River Floodplain',
  //   targetTownVillage: 'Jorve Rural Settlement & Sangamner Sub-Division',
  //   subDistrictDistrict: 'Sangamner Taluka, Ahilyanagar District',
  //   stateRegion: 'Maharashtra',
  //   disasterType: 'Flash Flood',
  //   riskLevel: 'Low',
  //   confidencePercentage: 28,
  //   coordinates: [19.5761, 74.2073],
  //   epicenterFocalPoint: 'Pravara River Un-embanked Agriculture Basin',
  //   historicalPatternMatch: '25.5% match with Seasonal River Basin Baseline',
  //   primaryAnomalyDriver: 'Standard Riverine Flow (Within Safe Threshold)',
  //   satelliteRadarSig: 'Sentinel-2 imagery confirms river width within safe limits',
  //   weatherCorrelation: 'Moderate localized showers 18mm/24h',
  //   topographyFactor: 'Central plateau river basin with active reservoir control',
  //   citizenAlertStatus: 'Monitoring Only',
  //   affectedPopulationEstimate: '8,900 Agricultural Basin Residents',
  //   xaiReasoning: 'Telemetry matches standard seasonal river levels in Central India. Low confidence of disaster threat (28%) as reservoir buffer remains intact.',
  //   socialGatheringHotspots: [
  //     {
  //       id: 'HOT-05-A',
  //       name: 'Sangamner Weekly Farmer Market',
  //       category: 'Bazar / Open Market',
  //       distanceKm: 0.6,
  //       coordinates: [19.5780, 74.2090],
  //       peakCrowdEstimate: '9,500 Farmers & Buyers',
  //       riskPriority: 'URGENT EVACUATION WARNING',
  //       evacuationDirective: 'Alert APMC Market Committee & inspect riverbank stalls.',
  //     },
  //     {
  //       id: 'HOT-05-B',
  //       name: 'Jorve Village Bus Stand & Commercial Plaza',
  //       category: 'Transit Hub / Railway Station',
  //       distanceKm: 0.9,
  //       coordinates: [19.5740, 74.2040],
  //       peakCrowdEstimate: '1,800 Villagers & Commuters',
  //       riskPriority: 'URGENT EVACUATION WARNING',
  //       evacuationDirective: 'Issue village PA alert for low-lying shop owners near riverbank.',
  //     },
  //   ],
  // },
  {
    id: 'HAZ-IND-06',
    name: 'Bhachau Fault Line Creep Sector',
    targetTownVillage: 'Sikra Rural Settlement & Bhachau Sub-Division',
    subDistrictDistrict: 'Bhachau Taluka, Kutch District',
    stateRegion: 'Gujarat',
    disasterType: 'Micro-Seismic',
    riskLevel: 'Low',
    confidencePercentage: 20,
    coordinates: [23.2984, 70.3541],
    epicenterFocalPoint: 'Katrol Hill Fault Line Creep Strain Point',
    historicalPatternMatch: '18.0% match with Background Fault Creep Signature',
    primaryAnomalyDriver: 'Low-magnitude tremor cluster (M2.1 - M2.4)',
    satelliteRadarSig: 'GPS ground array registers minor tectonic strain accumulation',
    weatherCorrelation: 'Dry weather conditions, zero hydrological pressure impact',
    topographyFactor: 'Arid salt flat fault zone with sparse settlements',
    citizenAlertStatus: 'Monitoring Only',
    affectedPopulationEstimate: '4,200 Rural Settlement Residents',
    xaiReasoning: 'Micro-seismic activity matches routine tectonic fault stress releases. Confidence of major seismic event is very low (20%).',
    socialGatheringHotspots: [
      {
        id: 'HOT-06-A',
        name: 'Bhachau Station Road Market',
        category: 'Bazar / Open Market',
        distanceKm: 0.8,
        coordinates: [23.3010, 70.3580],
        peakCrowdEstimate: '2,900 Traders',
        riskPriority: 'URGENT EVACUATION WARNING',
        evacuationDirective: 'Monitor tremor sensors & notify local shopkeeper association.',
      },
      {
        id: 'HOT-06-B',
        name: 'Sikra Highway Junction & Truck Stop',
        category: 'Transit Hub / Railway Station',
        distanceKm: 1.3,
        coordinates: [23.2950, 70.3490],
        peakCrowdEstimate: '1,400 Drivers & Vendors',
        riskPriority: 'URGENT EVACUATION WARNING',
        evacuationDirective: 'Instruct highway patrol to maintain clear evacuation routes.',
      },
    ],
  }
];

export async function fetchHazardZones(): Promise<HazardZone[]> {
  return Promise.resolve(INDIA_HAZARD_ZONES);
}

const BACKEND_URL = 'https://ai-powered-geospatial-reliability-and-1mxp.onrender.com';

export interface BackendInsight {
  id: number;
  source_id: number;
  title: string;
  summary: string;
  reliability_score: number;
  consistency_score: number;
  confidence_score: number;
  explanation: string;
  latitude?: number | null;
  longitude?: number | null;
  town_village?: string | null;
  district?: string | null;
  state?: string | null;
  created_at: string;
}
function inferDisasterType(title: string): HazardZone['disasterType'] {
  const t = title.toLowerCase();
  if (t.includes('earthquake') || t.includes('seismic') || t.includes('tremor') || t.includes('quake')) return 'Micro-Seismic';
  if (t.includes('landslide')) return 'Landslide';
  if (t.includes('flood')) return 'Flash Flood';
  if (t.includes('cyclone')) return 'Cyclone Surge';
  if (t.includes('wildfire') || t.includes('fire')) return 'Wildfire';
  return 'Flash Flood'; // fallback default
}


/**
 * Curated nearby social-gathering hotspots for each known live-insight
 * location, keyed by lowercase town/district name. Live insights come from
 * the backend with no hotspot data of their own (unlike the hand-authored
 * static demo zones below), so this fills that gap for the locations we
 * currently track. Coordinates are small offsets from each insight's own
 * lat/lon — close enough to read as "nearby" on the map.
 */
const _GUWAHATI_HOTSPOTS: SocialGatheringHotspot[] = [
  {
    id: 'HOT-LIVE-GHY-A', name: 'Fancy Bazar', category: 'Bazar / Open Market',
    distanceKm: 3.1, coordinates: [26.1833, 91.7458], peakCrowdEstimate: '6,000 Traders & Shoppers',
    riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
    evacuationDirective: 'Alert riverside market vendors given proximity to Brahmaputra basin flood risk.',
  },
  {
    id: 'HOT-LIVE-GHY-B', name: 'Guwahati Railway Station', category: 'Transit Hub / Railway Station',
    distanceKm: 4.5, coordinates: [26.1750, 91.7639], peakCrowdEstimate: '12,000+ Commuters',
    riskPriority: 'URGENT EVACUATION WARNING',
    evacuationDirective: 'Coordinate with NF Railway to prepare contingency schedules if water levels rise further.',
  },
];

const _LIVE_LOCATION_HOTSPOTS: Record<string, SocialGatheringHotspot[]> = {
  kolkata: [
    {
      id: 'HOT-LIVE-KOL-A', name: 'New Market Kolkata', category: 'Bazar / Open Market',
      distanceKm: 1.2, coordinates: [22.5626, 88.3522], peakCrowdEstimate: '8,500 Shoppers & Traders',
      riskPriority: 'URGENT EVACUATION WARNING',
      evacuationDirective: 'Alert market association and stage crowd-control at all entry points.',
    },
    {
      id: 'HOT-LIVE-KOL-B', name: 'Howrah Railway Station', category: 'Transit Hub / Railway Station',
      distanceKm: 2.6, coordinates: [22.5839, 88.3428], peakCrowdEstimate: '20,000+ Commuters',
      riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
      evacuationDirective: 'Coordinate with Railway Protection Force to manage platform evacuation routes.',
    },
  ],
  singrauli: [
    {
      id: 'HOT-LIVE-SGR-A', name: 'Singrauli Main Market (Baidhan)', category: 'Bazar / Open Market',
      distanceKm: 1.8, coordinates: [24.2038, 82.6742], peakCrowdEstimate: '3,000 Traders & Shoppers',
      riskPriority: 'URGENT EVACUATION WARNING',
      evacuationDirective: 'Notify local shopkeeper association and monitor seismic sensor readings.',
    },
  ],
  kurseong: [
    {
      id: 'HOT-LIVE-KUR-A', name: 'Kurseong Bazar & Toy Train Station', category: 'Transit Hub / Railway Station',
      distanceKm: 0.5, coordinates: [26.8800, 88.2762], peakCrowdEstimate: '1,800 Commuters & Tourists',
      riskPriority: 'URGENT EVACUATION WARNING',
      evacuationDirective: 'Coordinate with DHR staff to suspend toy-train operations if slope instability rises.',
    },
  ],
  hojai: [
    {
      id: 'HOT-LIVE-HOJ-A', name: 'Hojai Central Market', category: 'Bazar / Open Market',
      distanceKm: 0.9, coordinates: [26.0036, 92.8577], peakCrowdEstimate: '2,200 Traders & Shoppers',
      riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
      evacuationDirective: 'Issue flood alert to market association and pre-stage boats at known low-lying access points.',
    },
    {
      id: 'HOT-LIVE-HOJ-B', name: 'Hojai Bus Stand', category: 'Transit Hub / Railway Station',
      distanceKm: 1.1, coordinates: [26.0021, 92.8601], peakCrowdEstimate: '900 Commuters',
      riskPriority: 'URGENT EVACUATION WARNING',
      evacuationDirective: 'Maintain a clear evacuation corridor along the highway approach.',
    },
  ],
  // Guwahati insights sometimes geocode to a neighborhood (e.g. "Sawkuchi")
  // rather than the city name itself, so both keys point at the same data.
  guwahati: _GUWAHATI_HOTSPOTS,
  sawkuchi: _GUWAHATI_HOTSPOTS,
  'kamrup metropolitan': _GUWAHATI_HOTSPOTS,
  'new delhi': [
    {
      id: 'HOT-LIVE-DEL-A', name: 'Connaught Place', category: 'Shopping Mall / Commercial Hub',
      distanceKm: 2.0, coordinates: [28.6315, 77.2167], peakCrowdEstimate: '15,000+ Visitors',
      riskPriority: 'CRITICAL HIGH-DENSITY ALERT',
      evacuationDirective: 'Coordinate with Delhi Police to manage crowd flow if tremor intensity escalates.',
    },
    {
      id: 'HOT-LIVE-DEL-B', name: 'New Delhi Railway Station', category: 'Transit Hub / Railway Station',
      distanceKm: 1.4, coordinates: [28.6431, 77.2197], peakCrowdEstimate: '25,000+ Commuters',
      riskPriority: 'URGENT EVACUATION WARNING',
      evacuationDirective: 'Coordinate with Railway Protection Force on platform evacuation protocol.',
    },
  ],
};

function hotspotsForLiveInsight(insight: BackendInsight): SocialGatheringHotspot[] {
  const townKey = (insight.town_village ?? '').trim().toLowerCase();
  const districtKey = (insight.district ?? '').trim().toLowerCase();
  return _LIVE_LOCATION_HOTSPOTS[townKey] ?? _LIVE_LOCATION_HOTSPOTS[districtKey] ?? [];
}


function mapInsightToHazardZone(insight: BackendInsight): HazardZone {
  const riskLevel: 'Low' | 'Medium' | 'High' =
    insight.confidence_score >= 70 ? 'High' :
    insight.confidence_score >= 40 ? 'Medium' : 'Low';

  return {
    id: `LIVE-${insight.id}`,
    name: insight.title,
    isLive: true,
    targetTownVillage: insight.town_village ?? 'Not available (no reverse-geocoding source connected)',
    subDistrictDistrict: insight.district ?? 'Not available (no reverse-geocoding source connected)',
    stateRegion: insight.state ?? 'Not available (no reverse-geocoding source connected)',
    disasterType: inferDisasterType(insight.title),
    riskLevel,
    confidencePercentage: Math.round(insight.confidence_score),
    coordinates: [insight.latitude ?? 0, insight.longitude ?? 0],
    epicenterFocalPoint: insight.summary,
    historicalPatternMatch: 'Not available (no historical pattern-match source connected)',
    primaryAnomalyDriver: 'Not available (no anomaly-driver source connected)',
    satelliteRadarSig: 'Not available (no satellite data source connected)',
    weatherCorrelation: 'Not available (no weather data source connected)',
    topographyFactor: 'Not available (no topography data source connected)',
    citizenAlertStatus: insight.confidence_score < 50 ? 'Active Alert Issued' : 'Monitoring Only',
    affectedPopulationEstimate: 'Not available (no demographic data source connected)',
    xaiReasoning: insight.explanation,
    socialGatheringHotspots: hotspotsForLiveInsight(insight),
  };
}

export async function fetchLiveHazardZones(): Promise<HazardZone[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/insights`);
    if (!res.ok) return [];
    const data: BackendInsight[] = await res.json();
    return data.map(mapInsightToHazardZone);
  } catch {
    return [];
  }
}

/** Raw insights, most recent first — used by the live feed timeline, which
 *  needs created_at and hasn't been reshaped into a map-pin's HazardZone shape. */
export async function fetchRawInsights(): Promise<BackendInsight[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/insights`);
    if (!res.ok) return [];
    const data: BackendInsight[] = await res.json();
    return [...data].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  } catch {
    return [];
  }
}

export async function fetchAllHazardZones(): Promise<HazardZone[]> {
  const [mockZones, liveZones] = await Promise.all([
    fetchHazardZones(),
    fetchLiveHazardZones(),
  ]);
  return [...liveZones, ...mockZones];
}

export async function detectUserLocationAndCheckSurroundingHazards(): Promise<UserLocationHazardAssessment> {
  return new Promise((resolve) => {
    const defaultCoords: [number, number] = [19.0760, 72.8777];
    const findNearestAndAssess = (lat: number, lng: number, locName: string) => {
      let minDistance = Infinity;
      let nearest = INDIA_HAZARD_ZONES[0];

      INDIA_HAZARD_ZONES.forEach((zone) => {
        const dLat = (zone.coordinates[0] - lat) * (Math.PI / 180);
        const dLng = (zone.coordinates[1] - lng) * (Math.PI / 180);
        const a =
          Math.sin(dLat / 2) * Math.sin(dLat / 2) +
          Math.cos(lat * (Math.PI / 180)) *
            Math.cos(zone.coordinates[0] * (Math.PI / 180)) *
            Math.sin(dLng / 2) *
            Math.sin(dLng / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const dist = 6371 * c;

        if (dist < minDistance) {
          minDistance = dist;
          nearest = zone;
        }
      });

      const isDanger = nearest.riskLevel === 'High' || nearest.riskLevel === 'Medium';

      resolve({
        userLat: lat,
        userLng: lng,
        locationName: locName,
        nearestHazard: nearest,
        distanceKm: Math.round(minDistance),
        isDangerDetected: isDanger,
      });
    };

    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          findNearestAndAssess(
            Number(pos.coords.latitude.toFixed(4)),
            Number(pos.coords.longitude.toFixed(4)),
            'Detected Live Coordinates'
          );
        },
        () => {
          findNearestAndAssess(defaultCoords[0], defaultCoords[1], 'Localized Zone (Mumbai Coastal Sector)');
        },
        { timeout: 2500 }
      );
    } else {
      findNearestAndAssess(defaultCoords[0], defaultCoords[1], 'Localized Zone (Mumbai Coastal Sector)');
    }
  });
}
