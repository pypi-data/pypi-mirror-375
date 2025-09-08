import os
import json
import httpx
from fastmcp import FastMCP
from fastmcp.tools.tool_transform import ArgTransform, ToolTransformConfig, ArgTransformConfig

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_BASE_URL = "https://api.apollo.io/api/v1"

if not APOLLO_API_KEY:
    raise ValueError("APOLLO_API_KEY environment variable is required")

# Create an HTTP client for your API
client = httpx.AsyncClient(
    base_url=APOLLO_BASE_URL,
    headers={
        "X-Api-Key": APOLLO_API_KEY,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
)

# Load your OpenAPI spec
with open(os.path.join(os.path.dirname(__file__), 'schema.json'), ) as f:
    openapi_spec = json.load(f)

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="Apollo.io MCP Server",
    tool_transformations={
        "bulk_organization_enrichment": ToolTransformConfig(
            name="bulk_organization_enrichment",
            arguments={
                "domains[]": ArgTransformConfig(
                    name="domains",
                ),
            }
        ),
        "people_search": ToolTransformConfig(
            name="people_search",
            arguments={
                "person_titles[]": ArgTransformConfig(
                    name="person_titles",
                ),
                "person_locations[]": ArgTransformConfig(
                    name="person_locations",
                ),
                "person_seniorities[]": ArgTransformConfig(
                    name="person_seniorities",
                ),
                "organization_locations[]": ArgTransformConfig(
                    name="organization_locations",
                ),
                "q_organization_domains_list[]": ArgTransformConfig(
                    name="q_organization_domains_list",
                ),
                "contact_email_status[]": ArgTransformConfig(
                    name="contact_email_status",
                ),
                "organization_ids[]": ArgTransformConfig(
                    name="organization_ids",
                ),
                "organization_num_employees_ranges[]": ArgTransformConfig(
                    name="organization_num_employees_ranges",
                ),
                "revenue_range[min]": ArgTransformConfig(
                    name="revenue_range_min",
                ),
                "revenue_range[max]": ArgTransformConfig(
                    name="revenue_range_max",
                ),
                "currently_using_all_of_technology_uids[]": ArgTransformConfig(
                    name="currently_using_all_of_technology_uids",
                ),
                "currently_using_any_of_technology_uids[]": ArgTransformConfig(
                    name="currently_using_any_of_technology_uids",
                ),
                "currently_not_using_any_of_technology_uids[]": ArgTransformConfig(
                    name="currently_not_using_any_of_technology_uids",
                ),
                "q_organization_job_titles[]": ArgTransformConfig(
                    name="q_organization_job_titles",
                ),
                "organization_job_locations[]": ArgTransformConfig(
                    name="organization_job_locations",
                ),
                "organization_num_jobs_range[min]": ArgTransformConfig(
                    name="organization_num_jobs_range_min",
                ),
                "organization_num_jobs_range[max]": ArgTransformConfig(
                    name="organization_num_jobs_range_max",
                ),
                "organization_job_posted_at_range[min]": ArgTransformConfig(
                    name="organization_job_posted_at_range_min",
                ),
                "organization_job_posted_at_range[max]": ArgTransformConfig(
                    name="organization_job_posted_at_range_max",
                ),
            }
        ),
        "organization_search": ToolTransformConfig(
            name="organization_search",
            arguments={
                "organization_num_employees_ranges[]": ArgTransformConfig(
                    name="organization_num_employees_ranges",
                ),
                "organization_locations[]": ArgTransformConfig(
                    name="organization_locations",
                ),
                "organization_not_locations[]": ArgTransformConfig(
                    name="organization_not_locations",
                ),
                "revenue_range[min]": ArgTransformConfig(
                    name="revenue_range_min",
                ),
                "revenue_range[max]": ArgTransformConfig(
                    name="revenue_range_max",
                ),
                "currently_using_any_of_technology_uids[]": ArgTransformConfig(
                    name="currently_using_any_of_technology_uids",
                ),
                "q_organization_keyword_tags[]": ArgTransformConfig(
                    name="q_organization_keyword_tags",
                ),
                "organization_ids[]": ArgTransformConfig(
                    name="organization_ids",
                ),
                "latest_funding_amount_range[min]": ArgTransformConfig(
                    name="latest_funding_amount_range_min",
                ),
                "latest_funding_amount_range[max]": ArgTransformConfig(
                    name="latest_funding_amount_range_max",
                ),
                "total_funding_range[min]": ArgTransformConfig(
                    name="total_funding_range_min",
                ),
                "total_funding_range[max]": ArgTransformConfig(
                    name="total_funding_range_max",
                ),
                "latest_funding_date_range[min]": ArgTransformConfig(
                    name="latest_funding_date_range_min",
                ),
                "latest_funding_date_range[max]": ArgTransformConfig(
                    name="latest_funding_date_range_max",
                ),
                "q_organization_job_titles[]": ArgTransformConfig(
                    name="q_organization_job_titles",
                ),
                "organization_job_locations[]": ArgTransformConfig(
                    name="organization_job_locations",
                ),
                "organization_num_jobs_range[min]": ArgTransformConfig(
                    name="organization_num_jobs_range_min",
                ),
                "organization_num_jobs_range[max]": ArgTransformConfig(
                    name="organization_num_jobs_range_max",
                ),
                "organization_job_posted_at_range[min]": ArgTransformConfig(
                    name="organization_job_posted_at_range_min",
                ),
                "organization_job_posted_at_range[max]": ArgTransformConfig(
                    name="organization_job_posted_at_range_max",
                ),

            }
        ),
        "search_for_accounts": ToolTransformConfig(
            name="search_for_accounts",
            arguments={
                "account_stage_ids[]": ArgTransformConfig(
                    name="account_stage_ids",
                )
            }
        ),
        "update_account_stage": ToolTransformConfig(
            name="update_account_stage",
            arguments={
                "account_ids[]": ArgTransformConfig(
                    name="account_ids",
                )
            }
        ),
        "update_account_ownership": ToolTransformConfig(
            name="update_account_ownership",
            arguments={
                "account_ids[]": ArgTransformConfig(
                    name="account_ids",
                )
            }
        ),
        "create_a_contact": ToolTransformConfig(
            name="create_a_contact",
            arguments={
                "label_names[]": ArgTransformConfig(
                    name="label_names",
                )
            }
        ),
        "update_a_contact": ToolTransformConfig(
            name="update_a_contact",
            arguments={
                "label_names[]": ArgTransformConfig(
                    name="label_names",
                )
            }
        ),
        "search_for_contacts": ToolTransformConfig(
            name="search_for_contacts",
            arguments={
                "contact_stage_ids[]": ArgTransformConfig(
                    name="contact_stage_ids",
                )
            }
        ),
        "update_contact_stage": ToolTransformConfig(
            name="update_contact_stage",
            arguments={
                "contact_ids[]": ArgTransformConfig(
                    name="contact_ids",
                )
            }
        ),
        "update_contact_ownership": ToolTransformConfig(
            name="update_contact_ownership",
            arguments={
                "contact_ids[]": ArgTransformConfig(
                    name="contact_ids",
                )
            }
        ),
        "add_contacts_to_sequence": ToolTransformConfig(
            name="add_contacts_to_sequence",
            arguments={
                "contact_ids[]": ArgTransformConfig(
                    name="contact_ids",
                )
            }
        ),
        "update_contact_status_sequence": ToolTransformConfig(
            name="update_contact_status_sequence",
            arguments={
                "emailer_campaign_ids[]": ArgTransformConfig(
                    name="emailer_campaign_ids",
                ),
                "contact_ids[]": ArgTransformConfig(
                    name="contact_ids",
                )
            }
        ),
        "create_task": ToolTransformConfig(
            name="create_task",
            arguments={
                "contact_ids[]": ArgTransformConfig(
                    name="contact_ids",
                )
            }
        ),
        "search_tasks": ToolTransformConfig(
            name="search_tasks",
            arguments={
                "open_factor_names[]": ArgTransformConfig(
                    name="open_factor_names",
                )
            }
        ),
        "get_phone_callssearch": ToolTransformConfig(
            name="get_phone_callssearch",
            arguments={
                "date_range[max]": ArgTransformConfig(
                    name="date_range_max",
                ),
                "date_range[min]": ArgTransformConfig(
                    name="date_range_min",
                ),
                "duration[max]": ArgTransformConfig(
                    name="duration_max",
                ),
                "duration[min]": ArgTransformConfig(
                    name="duration_min",
                ),
                "user_ids[]": ArgTransformConfig(
                    name="user_ids",
                ),
                "contact_label_ids[]": ArgTransformConfig(
                    name="contact_label_ids",
                ),
                "phone_call_purpose_ids[]": ArgTransformConfig(
                    name="phone_call_purpose_ids",
                ),
                "phone_call_outcome_ids[]": ArgTransformConfig(
                    name="phone_call_outcome_ids",
                ),
            }
        ),
        "emailer_messagessearch": ToolTransformConfig(
            name="emailer_messagessearch",
            arguments={
                "emailer_message_stats[]": ArgTransformConfig(
                    name="emailer_message_stats",
                ),
                "emailer_message_reply_classes[]": ArgTransformConfig(
                    name="emailer_message_reply_classes",
                ),
                "user_ids[]": ArgTransformConfig(
                    name="user_ids",
                ),
                "emailer_campaign_ids[]": ArgTransformConfig(
                    name="emailer_campaign_ids",
                ),
                "not_emailer_campaign_ids[]": ArgTransformConfig(
                    name="not_emailer_campaign_ids",
                ),
                "emailerMessageDateRange[max]": ArgTransformConfig(
                    name="emailerMessageDateRange_max",
                ),
                "emailerMessageDateRange[min]": ArgTransformConfig(
                    name="emailerMessageDateRange_min",
                ),
                "not_sent_reason_cds[]": ArgTransformConfig(
                    name="not_sent_reason_cds",
                ),
            }
        ),
        "phonecalls_create": ToolTransformConfig(
            name="phonecalls_create",
            arguments={
                "user_id[]": ArgTransformConfig(
                    name="user_id",
                )
            }
        ),
        "put_phone_callsupdate": ToolTransformConfig(
            name="put_phone_callsupdate",
            arguments={
                "user_id[]": ArgTransformConfig(
                    name="user_id",
                )
            }
        ),
        "news_articles_search": ToolTransformConfig(
            name="news_articles_search",
            arguments={
                "organization_ids[]": ArgTransformConfig(
                    name="organization_ids",
                ),
                "categories[]": ArgTransformConfig(
                    name="categories",
                ),
                "published_at[min]": ArgTransformConfig(
                    name="published_at_min",
                ),
                "published_at[max]": ArgTransformConfig(
                    name="published_at_max",
                ),
            }
        ),
    }
)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
