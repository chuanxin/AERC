export interface GrantCreateRequest {
  name: string;
  id: string;
  phone: string;
  county: string;
  countyId: number | null;
  town: string;
  townId: number | null;
  village: string;
  villageId: number | null;
  address: string;
  undertracker: string;
  office: string;
  officeId: number | null;
  valid: boolean;
}


