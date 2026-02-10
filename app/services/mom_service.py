
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

from langchain_core.prompts import ChatPromptTemplate

from app.services.llms import LLMService
from app.schemas import (
    Attendees,
    GeneralSummaries,
    TopicSummaries,
    Facts,
    Decisions,
    ActionItems
)

# Define the State
class MomState(TypedDict):
    """
    Represents the state of the MoM generation process.
    """
    transcription: str
    
    # Extracted Data
    attendees: Attendees
    general_summaries: GeneralSummaries
    topic_summaries: TopicSummaries
    facts: Facts
    decisions: Decisions
    action_items: ActionItems


class MoMService:
    def __init__(self):
        self.llm_service = LLMService()
        # Use Groq for speed, or Mistral if preferred. 
        # Using a model with good context window and instruction following is key.
        # whisper-large-v3 is for audio, we need text model here.
        # Assuming LLMService initializes ChatGroq with a text model (e.g. llama3-70b-8192 or similar default)
        # We might need to specify model name if not default. 
        # For now using the client as is.
        self.llm = self.llm_service.groq_client 
        # self.llm = self.llm_service.mistral_client 

    # --- Node Functions ---

    def extract_attendees(self, state: MomState) -> dict:
        print("   -> Extracting Attendees...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at extracting meeting attendees from transcripts."),
            ("human", "Extract all attendees from the following transcript:\n\n{transcription}")
        ])
        chain = prompt | self.llm.with_structured_output(Attendees)
        result = chain.invoke({"transcription": state["transcription"]})
        return {"attendees": result}

    def extract_general_summaries(self, state: MomState) -> dict:
        print("   -> Extracting General Summaries...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at summarizing meetings. Create a high-level executive summary."),
            ("human", "Summarize the following transcript:\n\n{transcription}")
        ])
        chain = prompt | self.llm.with_structured_output(GeneralSummaries)
        result = chain.invoke({"transcription": state["transcription"]})
        return {"general_summaries": result}

    def extract_topic_summaries(self, state: MomState) -> dict:
        print("   -> Extracting Topic Summaries...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at summarizing specific topics from meetings."),
            ("human", "Identify and summarize key topics from the following transcript:\n\n{transcription}")
        ])
        chain = prompt | self.llm.with_structured_output(TopicSummaries)
        result = chain.invoke({"transcription": state["transcription"]})
        return {"topic_summaries": result}

    def extract_facts(self, state: MomState) -> dict:
        print("   -> Extracting Facts...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at extracting objective facts and metrics from meetings."),
            ("human", "Extract verifiable facts and data points from the following transcript:\n\n{transcription}")
        ])
        chain = prompt | self.llm.with_structured_output(Facts)
        result = chain.invoke({"transcription": state["transcription"]})
        return {"facts": result}

    def extract_decisions(self, state: MomState) -> dict:
        print("   -> Extracting Decisions (Context Aware)...")
        # Context building
        context = {
            "attendees": state.get("attendees").model_dump_json() if state.get("attendees") else "None",
            "general_summaries": state.get("general_summaries").model_dump_json() if state.get("general_summaries") else "None",
            "facts": state.get("facts").model_dump_json() if state.get("facts") else "None",
             # Topic summaries might be too large, but useful. Let's include if size permits.
             # For now, let's include it.
            "topic_summaries": state.get("topic_summaries").model_dump_json() if state.get("topic_summaries") else "None"
        }
        
        prompt_text = """
        Based on the transcript and the following context, extract the key decisions made.
        
        Context:
        Attendees: {attendees}
        General Summary: {general_summaries}
        Facts: {facts}
        Topics: {topic_summaries}
        
        Transcript:
        {transcription}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at identifying binding decisions in meetings. Use the provided context to aid extraction."),
            ("human", prompt_text)
        ])
        
        chain = prompt | self.llm.with_structured_output(Decisions)
        result = chain.invoke({
            "transcription": state["transcription"],
            **context
        })
        return {"decisions": result}

    def extract_action_items(self, state: MomState) -> dict:
        print("   -> Extracting Action Items (Full Context)...")
        # Context building including decisions now
        context = {
            "attendees": state.get("attendees").model_dump_json() if state.get("attendees") else "None",
            "decisions": state.get("decisions").model_dump_json() if state.get("decisions") else "None",
            "facts": state.get("facts").model_dump_json() if state.get("facts") else "None"
        }

        prompt_text = """
        Based on the transcript and the following context (including decisions made), extract actionable tasks and action items.
        
        Context:
        Attendees: {attendees}
        Decisions: {decisions}
        Facts: {facts}
        
        Transcript:
        {transcription}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at tracking action items and assigning tasks. Ensure action items align with decisions made."),
            ("human", prompt_text)
        ])

        chain = prompt | self.llm.with_structured_output(ActionItems)
        result = chain.invoke({
            "transcription": state["transcription"],
            **context
        })
        return {"action_items": result}

    # --- Graph Construction ---
    def build_graph(self):
        workflow = StateGraph(MomState)

        # Add Nodes
        workflow.add_node("extract_attendees", self.extract_attendees)
        workflow.add_node("extract_general_summaries", self.extract_general_summaries)
        workflow.add_node("extract_topic_summaries", self.extract_topic_summaries)
        workflow.add_node("extract_facts", self.extract_facts)
        
        workflow.add_node("extract_decisions", self.extract_decisions)
        workflow.add_node("extract_action_items", self.extract_action_items)

        # Edges
        # START -> Attendees
        workflow.add_edge(START, "extract_attendees")
        
        # Sequential Execution to avoid Rate Limits
        # Attendees -> Facts
        workflow.add_edge("extract_attendees", "extract_facts")
        
        # Facts -> General Summaries
        workflow.add_edge("extract_facts", "extract_general_summaries")
        
        # General Summaries -> Topic Summaries
        workflow.add_edge("extract_general_summaries", "extract_topic_summaries")
        
        # Topic Summaries -> Decisions (Context is built sequentially if needed, or state is accumulated)
        workflow.add_edge("extract_topic_summaries", "extract_decisions")

        # Decisions -> Action Items
        workflow.add_edge("extract_decisions", "extract_action_items")

        # Action Items -> END
        workflow.add_edge("extract_action_items", END)

        return workflow.compile()

    def generate_mom(self, transcription: str) -> MomState:
        """
        Executes the MoM generation workflow.
        """
        app = self.build_graph()
        result = app.invoke({"transcription": transcription})
        return result
