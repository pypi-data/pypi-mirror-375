from datetime import datetime
from nemo_library.adapter.hubspot.hubspot_object_type import HubSpotObjectType
from prefect import get_run_logger
from nemo_library.adapter.hubspot.symbols import DEAL_PROPERTIES_WITH_HISTORY
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary


class HubSpotTransform:
    """
    Class to handle transformation of data for the HubSpot adapter.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def transform_deals_plain(self) -> None:
        """
        Transform deals data for forecast call.
        """
        self.logger.info("Transforming deals data for forecast call")

        # Load extracted deals data
        filehandler = ETLFileHandler()
        deals = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.DEALS,
        )

        if not deals:
            raise ValueError("No deals data found to transform")

        # resolve mappings
        deals = self._resolve_mappings(deals)

        # enrich with company associations
        deals = self._add_company_associations(deals)

        # save transformed deals
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.TRANSFORM,
            data=deals,
            entity=HubSpotObjectType.DEALS,
        )

    def _resolve_mappings(self, deals):
        filehandler = ETLFileHandler()
        pipelines = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.PIPELINES,
        )
        if not pipelines:
            raise ValueError("No pipelines data found to transform")

        deal_owners = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.DEAL_OWNERS,
        )
        if not deal_owners:
            raise ValueError("No deal owners data found to transform")

        users = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.USERS,
        )
        if not users:
            raise ValueError("No users data found to transform")

        # Map pipeline_id -> pipeline_label
        pipeline_label_by_id = {}
        # Map (pipeline_id, stage_id) -> stage_label
        stage_label_by_pipeline_and_id = {}
        # Global fallback: stage_id -> stage_label (last one wins if duplicated)
        global_stage_label_by_id = {}
        # deal owner
        owner_label_by_id = {}

        for o in deal_owners:
            o_id = o.get("id")
            o_label = o.get("email")
            if o_id:
                owner_label_by_id[o_id] = o_label

        for u in users:
            u_id = u.get("id")
            u_label = u.get("email")
            if u_id:
                owner_label_by_id[u_id] = u_label

        for p in pipelines.get("results", []):
            p_id = p.get("id")
            p_label = p.get("label")
            if p_id:
                pipeline_label_by_id[p_id] = p_label
            for s in p.get("stages", []):
                s_id = s.get("id")
                s_label = s.get("label")
                if p_id and s_id:
                    stage_label_by_pipeline_and_id[(p_id, s_id)] = s_label
                if s_id:
                    global_stage_label_by_id[s_id] = s_label

        # Track unresolved mappings
        unresolved_stages = set()
        unresolved_pipelines = set()
        unresolved_owners = set()

        # Map deal stage, pipeline, and owner
        for deal in deals:
            stage_key = (deal.get("pipeline"), deal.get("dealstage"))
            if stage_key in stage_label_by_pipeline_and_id:
                deal["dealstage"] = stage_label_by_pipeline_and_id[stage_key]
            else:
                unresolved_stages.add(stage_key)

            pipeline_key = deal.get("pipeline")
            if pipeline_key in pipeline_label_by_id:
                deal["pipeline"] = pipeline_label_by_id[pipeline_key]
            else:
                unresolved_pipelines.add(pipeline_key)

            owner_key = deal.get("hubspot_owner_id")
            if owner_key in owner_label_by_id:
                deal["hubspot_owner_id"] = owner_label_by_id[owner_key]
            else:
                unresolved_owners.add(owner_key)

        # Create a summary dictionary for unresolved mappings
        unresolved_summary = {
            "dealstages": list(unresolved_stages),
            "pipelines": list(unresolved_pipelines),
            "owners": list(unresolved_owners),
        }

        if unresolved_summary:
            self.logger.warning(f"Unresolved mappings found: {unresolved_summary}")

        return deals

    def _add_company_associations(self, deals):
        filehandler = ETLFileHandler()
        deal_companies = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.DEAL_COMPANIES,
        )

        if not deal_companies:
            raise ValueError("No deal companies data found to transform")

        company_details = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.COMPANY_DETAILS,
        )
        if not company_details:
            raise ValueError("No company details data found to transform")
        compdetail = {}
        for detail in company_details:
            compdetail[detail.get("company_id")] = detail

        # Map deal_id -> company_ids (still collect all, just in case)
        company_ids_by_deal_id = {}
        for association in deal_companies:
            company_ids_by_deal_id.setdefault(association.get("deal_id"), []).append(
                association.get("company_id")
            )

        # Enrich deals with single company_id property
        for deal in deals:
            company_ids = company_ids_by_deal_id.get(deal.get("id"), [])
            if company_ids:
                deal["company_id"] = company_ids[0]  # take the first one
                detail = compdetail.get(deal["company_id"])
                for key, value in detail.items():
                    deal[key] = value
                if len(company_ids) > 1:
                    self.logger.warning(
                        f"Deal ID {deal.get('id')} is associated with multiple companies: {company_ids}. "
                        f"Using the first one: {deal['company_id']}"
                    )
            else:
                deal["company_id"] = None

        return deals

    def transform_deals_with_history(self) -> None:
        """
        Transform deals data for forecast call.
        """
        self.logger.info("Transforming deals data for forecast call")

        # Load extracted deals data
        filehandler = ETLFileHandler()
        deals = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.TRANSFORM,
            entity=HubSpotObjectType.DEALS,
        )

        if not deals:
            raise ValueError("No deals data found to transform")

        deal_history = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.DEAL_HISTORY,
        )

        if not deal_history:
            raise ValueError("No deal history data found to transform")

        # join deal with history

        joined_deals = []
        for deal in deals:

            # template for copying
            masterdeal = deal.copy()

            # add history to deal
            deal_id = deal.get("id")
            history = deal_history.get(deal_id, {}).get("history")
            deal["history"] = history

            deal_changes = {}
            for prop in DEAL_PROPERTIES_WITH_HISTORY:
                for change in history.get(prop, []):
                    deal_changes[change.get("timestamp")] = {prop: change.get("value")}

            sorted_changes = [
                {"timestamp": datetime.fromisoformat(ts.replace("Z", "+00:00")), **vals}
                for ts, vals in sorted(
                    deal_changes.items(),
                    key=lambda x: datetime.fromisoformat(x[0].replace("Z", "+00:00")),
                )
            ]
            deal["changes"] = sorted_changes   
                     
            # clean up template 
            for prop in DEAL_PROPERTIES_WITH_HISTORY:
                masterdeal[prop] = None

            # now start copying changes to joined deal
            joineddeal = masterdeal.copy()
            for change in sorted_changes:
                joineddeal = joineddeal.copy()
                joineddeal["changedate"] = change["timestamp"]
                for prop in DEAL_PROPERTIES_WITH_HISTORY:
                    if prop in change:
                        joineddeal[prop] = change[prop]
                joined_deals.append(joineddeal)

        # save transformed deals
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.TRANSFORM,
            data=deals,
            entity=HubSpotObjectType.DEALS_WITH_HISTORY,
        )
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.TRANSFORM,
            data=joined_deals,
            entity=HubSpotObjectType.JOINED_DEALS_WITH_HISTORY,
        )
