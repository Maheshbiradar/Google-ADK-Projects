from google.adk.agents import LlmAgent, ParallelAgent, LoopAgent, SequentialAgent

from competitive_intelligence_pipeline.company_extractor_agent import company_extractor_agent
from competitive_intelligence_pipeline.competitor_agent import competitor_agent
from competitive_intelligence_pipeline.evaluator_agent import evaluator_agent
from competitive_intelligence_pipeline.financial_agent import financial_agent
from competitive_intelligence_pipeline.news_agent import news_agent
from competitive_intelligence_pipeline.report_agent import report_agent
from competitive_intelligence_pipeline.constants import LOOP_MAX_ITERATIONS

research_parallel = ParallelAgent(
    name="research_parallel",
    sub_agents=[news_agent, financial_agent, competitor_agent],
)

research_loop = LoopAgent(
    name="research_loop",
    sub_agents=[research_parallel, evaluator_agent],
    max_iterations=LOOP_MAX_ITERATIONS,
)

competitive_intelligence_pipeline = SequentialAgent(
    name="competitive_intelligence_pipeline",
    sub_agents=[company_extractor_agent, research_loop, report_agent],
)
