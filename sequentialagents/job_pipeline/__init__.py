from .agent import job_pipeline as root_agent


# User provides: job_input

# Step 01 — research_agent
#     reads:  job_input[company] and job_input[role]
#     does:   research the company and role using google_search
#     writes: research_results

# Step 02 — fit_agent
#     reads:  research_results
#     does:   analyze the research results to determine fit for the role
#     writes: fit_report

# Step 03 — cover_letter_agent
#     reads:  fit_report
#     does:   generate a personalized cover letter based on the fit report
#     writes: cover_letter

# User sees: cover_letter
