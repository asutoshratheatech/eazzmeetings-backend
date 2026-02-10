from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class GenerateMoMRequest(BaseModel):
    transcription: str
    meeting_link: HttpUrl
    audio_url: HttpUrl
    meeting_date: str
    meeting_time: str
    meeting_duration: str

class Attendee(BaseModel):
    name: str=Field(...,description='Name of the attendee')
    designation:Optional[str]=Field(None,description='Designation of the attendee if it was mentioned in the transcript')
    company:Optional[str]=Field(None,description='Company of the attendee if it was mentioned in the transcript')

class Attendees(BaseModel):
    attendees: List[Attendee] = Field(
        default_factory=list,
        description='List and details of attendees who attended the meeting'
    )

# Agenda Of the Meeting
class Agenda(BaseModel):
    """
    A specific topic or agenda item discussed during the meeting.
    """
    topic_title: str = Field(
        ..., 
        description="A short, descriptive headline for the topic being discussed. Example: 'Q3 Marketing Strategy' or 'Server Migration Issues'."
    )
    topic_description: str = Field(
        ...,
        description="A brief summary of what this topic is about. This should be a single sentence that captures the essence of the discussion point.")

    by_who: Optional[list[str]] = Field(
        None, 
        description="The name of the primary person leading this specific discussion or presenting the slides. If multiple people spoke equally, add them all."
    )
    is_predetermined: Optional[bool] = Field(
        None, 
        description="True if this agenda item was planned and listed in the meeting invite or agenda document. False if it was spontaneously added during the meeting. None if unknown."
    )

class Agendas(BaseModel):
    """
    The official record of the meeting agendas. This model captures the context ffor the agenda and its relvant contributers and if it was pre-determined or not.  
    """

    agendas: List[Agenda] = Field(
        default_factory=list, 
        description="The core agendas of the meeting. Break down the transcript into distinct agendas. Each agendas must have its own entry in this list."
    )

class Decision(BaseModel):
    """
    A specific conclusion or ruling agreed upon during the meeting.
    """
    decision_headline: str = Field(
        ..., 
        description="A short, bold title for the decision. Example: 'Approved Q3 Budget' or 'Selected AWS as Cloud Provider'."
    )
    description: str = Field(
        ...,
        description="A detailed explanation of what was decided. Include specific numbers, final choices, or policy changes. Ensure this is distinct from the rationale."
    )
    rationale: Optional[str] = Field(
        None,
        description="The 'Why' behind the decision. Briefly explain the reasoning, data, or debate that led to this conclusion."
    )
    stakeholders: Optional[List[str]] = Field(
        None,
        description="List of specific names who explicitly agreed to or authorized this decision. If it was a general consensus, leave empty."
    )

class Decisions(BaseModel):
    """
    The collection of all binding decisions made.
    """
    decisions: List[Decision] = Field(
        default_factory=list,
        description="Extract all final decisions. Ignore tentative suggestions or items tabled for later."
    )

class ActionItem(BaseModel):
    """
    A task or follow-up activity assigned to a person or team.
    """
    task_title: str = Field(
        ...,
        description="A short, verb-led title for the task. Example: 'Email client', 'Fix bug #404', 'Draft proposal'."
    )
    description: str = Field(
        ...,
        description="A comprehensive description of the task requirements. Include any specific constraints or details mentioned in the meeting."
    )
    assignees: Optional[List[str]] = Field(
        None,
        description="The names of the people responsible for completing this task. If assigned to a department (e.g., 'Marketing'), use that instead of a name."
    )
    due_date: Optional[str] = Field(
        None,
        description="The specific deadline mentioned (e.g., 'Next Friday', 'End of Q1', '2023-10-15'). If no date is mentioned, return None."
    )

class ActionItems(BaseModel):
    """
    The To-Do list generated from the meeting.
    """
    action_items: List[ActionItem] = Field(
        default_factory=list,
        description="Extract all actionable tasks. Ensure every item implies an output or an action to be taken."
    )

class Fact(BaseModel):
    """
    A verifiable piece of information, statistic, or data point mentioned.
    """
    topic_context: str = Field(
        ...,
        description="The general topic this fact relates to. Example: 'Q3 Financials', 'User Growth', 'Competitor Analysis'."
    )
    description: str = Field(
        ...,
        description="The detailed fact itself. Preserve specific numbers, percentages, dates, or technical specifications exactly as spoken."
    )
    source: Optional[str] = Field(
        None,
        description="Who stated this fact? Useful for attribution if the fact is disputed later."
    )

class Facts(BaseModel):
    """
    A collection of objective data points and confirmed statements.
    """
    facts: List[Fact] = Field(
        default_factory=list,
        description="Extract objective truths, metrics, and status updates. Do not include opinions or predictions."
    )

class TopicSummary(BaseModel):
    """
    A detailed summary of a specific agenda topic.
    """
    related_topic_title: str = Field(
        ...,
    description="This must match one of the 'topic_titles' from the Agenda list exactly. It links this summary to the specific agenda item."
    )
    description: str = Field(
        ...,
    description="A comprehensive paragraph summarizing the discussion for this specific topic. Include the main challenges discussed, arguments made, and the general sentiment."
    )
    key_takeaways: List[str] = Field(
        default_factory=list,
    description="A list of 3-5 bullet points highlighting the most critical aspects of this specific discussion."
    )

class TopicSummaries(BaseModel):
    """
    Structured summaries broken down by agenda item.
    """
    topic_summaries: List[TopicSummary] = Field(
        default_factory=list,
        description="Generate a summary object for every major topic discussed in the transcript."
    )

class GeneralSummary(BaseModel):
    """
    High-level executive summary of the entire meeting.
    """
    executive_overview: str = Field(
        ...,
        description="A concise paragraph (3-5 sentences) summarizing the main purpose and outcome of the meeting. Assume the reader is an executive who needs the 'bottom line'."
    )
    meeting_sentiment: str = Field(
        ...,
        description="Describe the overall tone of the meeting. Examples: 'Productive and optimistic', 'Tense and debate-heavy', 'Informational and low-energy'."
    )

class GeneralSummaries(BaseModel):
    """
    A collection of high-level executive summaries of the entire meeting.
    """
    general_summaries: List[GeneralSummary] = Field(
        default_factory=list,
        description="Extract all high-level executive summaries."
    )