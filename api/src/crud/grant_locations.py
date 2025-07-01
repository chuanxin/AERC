
import logging
from typing import List, Dict, Any
from tortoise.transactions import in_transaction
from psycopg2.extras import Json

from src.database.models import Grants, GrantLocations

logger = logging.getLogger(__name__)

async def sync_grant_locations(grant_id: int, step2_data: Dict[str, Any]):
    """
    Synchronizes the location data for a given grant based on step 2 data.
    This function performs an 'upsert' for current locations and 'prunes' old ones.

    Args:
        grant_id: The ID of the grant to synchronize.
        step2_data: The data from step 2, expected to contain a list of land parcels.
    """
    # The 'lands' key might vary, adjust if necessary based on actual frontend data structure
    land_parcels = step2_data.get('lands', [])

    if not isinstance(land_parcels, list):
        logger.warning(f"Step 2 data for grant {grant_id} does not contain a valid list of lands.")
        return

    current_location_keys = set()

    async with in_transaction() as conn:
        for parcel in land_parcels:
            try:
                # Extract necessary fields
                land_section = parcel.get('land_section')
                land_number = parcel.get('land_number')
                address_data = parcel.get('facilityAddress', {})
                longitude = address_data.get('longitude')
                latitude = address_data.get('latitude')

                # Validate required fields
                if not all([land_section, land_number, longitude, latitude]):
                    logger.warning(f"Skipping parcel due to missing data: {parcel}")
                    continue

                # Create a unique key for this location
                location_key = f"{grant_id}_{land_section}_{land_number}"
                current_location_keys.add(location_key)

                # Prepare data for upsert
                geom = f"POINT({float(longitude)} {float(latitude)})"
                
                # Extract other relevant data
                grant = await Grants.get(id=grant_id)
                applicant_name = grant.applicant_name
                apply_year = grant.year
                case_status = grant.status
                comment = f"Facility Address: {address_data.get('county', '')} {address_data.get('town', '')} {address_data.get('address', '')}"
                meta_data = {
                    "land_area": parcel.get('land_area'),
                    "facility_area": parcel.get('facility_area'),
                    "land_type_text": parcel.get('land_type_text')
                }

                # SQL for UPSERT
                sql = """
                INSERT INTO grant_locations (
                    grant_id, source_system, source_id, land_section, land_number, geom, 
                    applicant_name, apply_year, case_status, comment, meta_data, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                ON CONFLICT (grant_id, land_section, land_number) DO UPDATE SET
                    geom = EXCLUDED.geom,
                    applicant_name = EXCLUDED.applicant_name,
                    apply_year = EXCLUDED.apply_year,
                    case_status = EXCLUDED.case_status,
                    comment = EXCLUDED.comment,
                    meta_data = EXCLUDED.meta_data,
                    updated_at = NOW();
                """
                
                await conn.execute_script(
                    sql,
                    grant_id, 'new_aerc', str(grant_id), land_section, land_number, geom,
                    applicant_name, apply_year, case_status, comment, Json(meta_data)
                )

            except Exception as e:
                logger.error(f"Error processing parcel for grant {grant_id}: {parcel}. Error: {e}")

        # Pruning: Delete locations associated with this grant that are no longer present
        if current_location_keys:
            # Build a query to find all locations for the current grant
            existing_locations_query = "SELECT id, grant_id, land_section, land_number FROM grant_locations WHERE grant_id = $1"
            existing_locations = await conn.fetch(existing_locations_query, grant_id)

            locations_to_delete = []
            for loc in existing_locations:
                key = f"{loc['grant_id']}_{loc['land_section']}_{loc['land_number']}"
                if key not in current_location_keys:
                    locations_to_delete.append(loc['id'])
            
            if locations_to_delete:
                delete_query = "DELETE FROM grant_locations WHERE id = ANY($1::int[])"
                await conn.execute_script(delete_query, locations_to_delete)
                logger.info(f"Pruned {len(locations_to_delete)} old locations for grant {grant_id}.")

    logger.info(f"Synchronization complete for grant {grant_id}.")
