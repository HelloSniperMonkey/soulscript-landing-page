import os
from dotenv import load_dotenv
from google import genai
import json
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
import re
import pandas as pd
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle


import os
from dotenv import load_dotenv
from google import genai
import json
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from math import pi
from datetime import datetime
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# Load environment variables
load_dotenv()

# Read the API key from the environment
api_key = os.getenv("NEXT_PUBLIC_GEMINI_API_KEY")

# Initialize the genai client with the API key
client = genai.Client(api_key=api_key)
# Set credentials for Vertex AI
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/hackathons-423418-ca6c603344c4.json"

# Initialize Firebase Admin
cred = credentials.Certificate("secrets/service.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore client using the same credentials
db = firestore.Client(credentials=cred.get_credential(), project=cred.project_id)

EMOTIONS = ["Joy", "Sadness", "Anger", "Fear", "Surprise", "Disgust", "Neutral"]
def json_to_md(authID):

    """
    Convert JSON data to Markdown format using Gemini API.
    """
    prompt = """
    
    # Role  
    You are an intelligent system designed to extract and organize key information from unstructured text. Your objective is to identify relevant details and present them in a structured **Markdown format** for clear readability.  

    ## Task  
    Analyze the given input and extract meaningful insights related to:  
    - Personal background  
    - Experiences  
    - Lifestyle  
    - Relationships  
    - Overall well-being  

    Present the extracted information **exclusively in Markdown format**, ensuring proper use of headers, lists, and bold text where necessary.  
    Dont put the final output inside ```markdown   ```
    ## Guidelines  
    - Capture relevant personal and situational details.  
    - Identify recurring themes or concerns.  
    - Use appropriate Markdown syntax (e.g., `#`, `##`, `-`, `**bold**`).  
    - Ensure logical structuring for easy interpretation.  
    - If information is incomplete or unclear, infer context when reasonable.  
    -Dont put the final output inside ```markdown   ```




    """

    #document_id = authId
    document_id = authID

    # Fetch the document
    doc_ref = db.collection('users').document(document_id)
    doc = doc_ref.get()

    # Check if the document exists
    if doc.exists:
        data = doc.to_dict()
        user_history = data.get('userHistory')
        
        
        prompt += json.dumps(user_history, indent=2)

    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text if response else "Error generating Markdown."
    except Exception as e:
        return f"Error: {str(e)}"


def data_chat_extraction(authId, response_format="json"):
    prompt = """
**#role**  
You are an advanced data extraction system designed to process therapy questionnaire responses and convert them into structured JSON format. Your goal is to extract key details while maintaining accuracy, completeness, and logical structuring.  

**#task**  
1. Extract essential details from the provided therapy questionnaire responses.  
2. Structure the output in JSON format with the following fields:  
   - **Personal Information**: Name, Age, Gender, Contact  
   - **Employment & Lifestyle**: Employment Status, Relationship Status, Daily Routine  
   - **Mental Health History**: Past Diagnoses, Previous Treatments, Family History of Mental Health Conditions  
   - **Trauma History**: Significant Life Events, Impact, Coping Mechanisms  
   - **Behavioral Patterns**: Substance Use, Addiction or Compulsive Behaviors  
   - **Support System**: Social Support, Family & Friends' Role  
   - Other relevant details such as stressors, triggers, current emotional state, and therapy goals should be included naturally without using a generic label like "Additional Insights."  
3. If any responses are missing or unclear, mark the respective field as `"unclear"`.  
4. If the user doesn't want to respond to any question, then please mention that the user doesn't want to share that information.  
5. Ensure data is clean, structured, and properly formatted in JSON.  

**#critics**  
- Extract all relevant insights without misinterpretation.  
- Avoid unnecessary labels such as "Additional Insights" and instead integrate those details naturally into the JSON structure.  
- Ensure logical structuring, clarity, and accuracy, especially when handling missing or ambiguous responses.  
- Keep responses concise yet comprehensive in the JSON output.  
- Don't put the final output inside ```json   ```
    
Input:
"""

    document_id = authId
    doc_ref = db.collection('users').document(document_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": "Document not found"}

    data = doc.to_dict()
    user_history = data.get('userHistory')

    if not user_history:
        return {"error": "User history not found"}

    prompt += json.dumps(user_history, indent=2)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    response_text = response.candidates[0].content.parts[0].text.strip()
    response_text = response_text.replace("```json", "").replace("```", "")

    if response_format == "json":
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r"{[\s\S]*}", response_text)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    return json.loads(json_str)
                except:
                    pass
            return {
                "error": "Could not parse response",
                "raw_response": response_text,
            }
    else:
        return response_text




import pandas as pd
import json
from google.cloud import firestore


def analyze_with_llm(prompt, system_prompt="You are an expert psychologist analyzing journal entries."):
    full_prompt = f"{system_prompt}\n\n{prompt}"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[full_prompt],  # <-- must be a list of strings or Part instances
       
    )

    return response.text


# Your analysis pipeline
def analyze_journal_entries(authId):
    # Firestore client
    db = firestore.Client(credentials=cred.get_credential(), project=cred.project_id)

    # Fetch latest 10 journal entries for the user
    journal_ref = db.collection("users").document(authId).collection("journalEntries")
    query = journal_ref.order_by("date", direction=firestore.Query.DESCENDING).limit(5)
    snapshot = query.stream()

    # Convert to DataFrame-compatible structure
    records = []
    for doc in snapshot:
        data = doc.to_dict()
        records.append({
            "_id": doc.id,
            "title": data.get("title", ""),
            "date": data.get("date"),
            "content": data.get("content", "")
        })

    if not records:
        return pd.DataFrame()

    entries_df = pd.DataFrame(records)

    # Your existing analysis logic continues here
    analysis_results = []
    for _, entry in entries_df.iterrows():
        analysis_prompt = f"""
        Analyze this journal entry as a psychologist. Focus on key insights and actionable takeaways:

        Title: {entry['title']}
        Date: {entry['date']}
        Content: {entry['content']}

        Provide a concise yet comprehensive analysis covering:
        1. Emotional state (primary and secondary emotions)
        2. Cognitive patterns (positive/negative, rational/irrational)
        3. Stress indicators and coping mechanisms
        4. Notable behavioral patterns
        5. Key concerns or growth opportunities
        6. Specific recommendations for improvement

        Format your response with clear bullet points for each category.
        """
        analysis_text = analyze_with_llm(analysis_prompt)

        summary_prompt = f"""
        Summarize this psychological analysis into 1-2 key actionable insights from the journal entry:
        {analysis_text}

        Focus on the most important takeaways that the journal writer should pay attention to.
        Format as bullet points.
        """
        summary_text = analyze_with_llm(summary_prompt)

        emotion_prompt = f"""
        Analyze this journal entry and quantify the emotional content:
        {entry['content']}

        Return ONLY a JSON dictionary with values between 0-1 for these emotions: 
        {EMOTIONS}
        Example: {{"Joy": 0.5, "Sadness": 0.3, ...}}
        """
        try:
            emotion_json = analyze_with_llm(
                emotion_prompt,
                system_prompt="You are an emotion analysis tool. Return ONLY valid JSON.",
            )
            emotion_data = json.loads(emotion_json.strip("`").replace("json\n", ""))
        except:
            emotion_data = {e: 0 for e in EMOTIONS}

        analysis_results.append({
            "entry_id": entry["_id"],
            "date": entry["date"],
            "title": entry["title"],
            "analysis": analysis_text,
            "summary": summary_text,
            "emotions": emotion_data,
        })

    return json.dumps(analysis_results, indent=2, default=str)


# Set modern visualization style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

def analyze_with_llm_1(prompt, system_prompt="You are an expert psychologist analyzing journal entries."):
    full_prompt = f"{system_prompt}\n\n{prompt}"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[full_prompt],  # <-- must be a list of strings or Part instances
       
    )

    return response.text

def generate_visualizations(analysis_df,filename):
    """Generate professional visualizations with proper error handling"""
    try:
        nltk.download("vader_lexicon", quiet=True)
        sia = SentimentIntensityAnalyzer()
    except Exception as e:
        print(f"Error initializing sentiment analyzer: {e}")
        return []

    chart_paths = []
    
    # Set consistent color palette and style
    colors_palette = ["#4361EE", "#3A0CA3", "#7209B7", "#F72585", "#4CC9F0"]
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['axes.facecolor'] = '#F8F9FA'
    plt.rcParams['figure.facecolor'] = 'white'

    # 1. Sentiment Trend Chart
    sentiment_scores = []
    for _, row in analysis_df.iterrows():
        try:
            text = f"{row['title']} {row.get('content', '')} {row.get('analysis', '')}"
            sentiment = sia.polarity_scores(text)
            sentiment["date"] = row["date"].date() if hasattr(row["date"], 'date') else row["date"]
            sentiment_scores.append(sentiment)
        except Exception as e:
            print(f"Error analyzing sentiment for entry {row.get('title')}: {e}")

    if not sentiment_scores:
        print("Warning: No valid sentiment scores generated")
        return []

    sentiment_df = pd.DataFrame(sentiment_scores)

    # Handle single entry case
    if len(sentiment_df) > 1:
        daily_sentiment = sentiment_df.groupby("date").mean()
    else:
        daily_sentiment = sentiment_df.set_index("date")

    plt.figure(figsize=(10, 5))
    ax = plt.gca()

    # Smooth line for trend with gradient fill
    if len(daily_sentiment) > 1:
        daily_sentiment["compound_smooth"] = (
            daily_sentiment["compound"].rolling(window=2, min_periods=1).mean()
        )
        line = ax.plot(
            daily_sentiment.index,
            daily_sentiment["compound_smooth"],
            marker="o",
            color=colors_palette[0],
            linewidth=2.5,
            markersize=8,
        )
        # Add gradient fill below the line
        ax.fill_between(
            daily_sentiment.index, 
            daily_sentiment["compound_smooth"], 
            alpha=0.3, 
            color=colors_palette[0]
        )
    else:
        ax.bar(
            daily_sentiment.index,
            daily_sentiment["compound"],
            color=colors_palette[0],
            width=0.5,
            alpha=0.8,
        )

    # Formatting
    ax.set_title("Mood Trend Over Time", pad=15, fontsize=16, fontweight='bold')
    ax.set_xlabel("Date", labelpad=10, fontsize=12)
    ax.set_ylabel("Sentiment Score", labelpad=10, fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    
    # Add reference line at zero
    plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    
    # Add annotations for extreme values
    if len(daily_sentiment) > 1:
        max_idx = daily_sentiment["compound_smooth"].idxmax()
        min_idx = daily_sentiment["compound_smooth"].idxmin()
        
        ax.annotate(
            f"{daily_sentiment['compound_smooth'][max_idx]:.2f}",
            xy=(max_idx, daily_sentiment["compound_smooth"][max_idx]),
            xytext=(0, 10),
            textcoords="offset points",
            ha='center',
            va='bottom',
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
        )
        
        ax.annotate(
            f"{daily_sentiment['compound_smooth'][min_idx]:.2f}",
            xy=(min_idx, daily_sentiment["compound_smooth"][min_idx]),
            xytext=(0, -15),
            textcoords="offset points",
            ha='center',
            va='top',
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
        )
    ## gen a fstring


    plt.tight_layout()
    plt.savefig(f"{filename}-mood_trend.png", dpi=300, bbox_inches="tight")
    chart_paths.append(f"{filename}-mood_trend.png")
    plt.close()

    # 2. Emotion Analysis
    try:
        # Process emotion data with validation
        valid_emotions = []
        for _, row in analysis_df.iterrows():
            if isinstance(row.get("emotions"), dict):
                emotions = {
                    k: float(v)
                    for k, v in row["emotions"].items()
                    if k in EMOTIONS and 0 <= float(v) <= 1
                }
                if emotions:
                    emotions["date"] = row["date"].date() if hasattr(row["date"], 'date') else row["date"]
                    valid_emotions.append(emotions)

        if not valid_emotions:
            print("Warning: No valid emotion data found")
            return chart_paths

        emotion_df = pd.DataFrame(valid_emotions)

        # Calculate mean emotion scores
        emotion_means = emotion_df[EMOTIONS].mean().sort_values(ascending=False)

        # Emotion Composition Chart - Horizontal bars with gradient
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        
        # Create gradient bars
        for i, (emotion, value) in enumerate(emotion_means.items()):
            bar = ax.barh(
                emotion, 
                value, 
                color=colors_palette[i % len(colors_palette)],
                edgecolor='white',
                linewidth=0.7,
                alpha=0.8,
                height=0.6
            )
            
            # Add value labels
            ax.text(
                value + 0.02, 
                i, 
                f"{value:.2f}", 
                va='center',
                fontsize=10,
                fontweight='bold'
            )

        ax.set_title("Emotional Composition", pad=15, fontsize=16, fontweight='bold')
        ax.set_xlabel("Average Intensity (0-1)", labelpad=10, fontsize=12)
        ax.set_xlim(0, 1.1)
        ax.set_ylabel("")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{filename}-emotional_composition.png", dpi=300, bbox_inches="tight")
        chart_paths.append(f"{filename}-emotional_composition.png")
        plt.close()

        # 3. Emotion Radar Chart with improved styling
        if len(emotion_df) > 1:
            plt.figure(figsize=(8, 8), facecolor='white')
            ax = plt.subplot(111, polar=True)

            # Prepare data
            categories = EMOTIONS
            N = len(categories)
            angles = [n / float(N) * 2 * pi for n in range(N)]
            angles += angles[:1]

            # Add background grid with custom styling
            ax.set_theta_offset(pi / 2)
            ax.set_theta_direction(-1)
            ax.set_rlabel_position(0)
            
            # Add circular gridlines
            for y in [0.2, 0.4, 0.6, 0.8]:
                ax.plot(angles, [y] * (N + 1), color="grey", alpha=0.1, linewidth=0.5)
            
            # Add category lines
            for i in range(N):
                ax.plot([angles[i], angles[i]], [0, 1], color="grey", alpha=0.1, linewidth=0.5)

            # Plot each day with custom styling
            for i, (_, row) in enumerate(emotion_df.iterrows()):
                values = row[categories].values.flatten().tolist()
                values += values[:1]
                
                # Plot line
                ax.plot(
                    angles,
                    values,
                    linewidth=2,
                    linestyle="solid",
                    label=str(row["date"]),
                    color=colors_palette[i % len(colors_palette)],
                    alpha=0.8,
                )
                
                # Fill area
                ax.fill(
                    angles, 
                    values, 
                    color=colors_palette[i % len(colors_palette)],
                    alpha=0.1
                )

            # Formatting
            plt.xticks(angles[:-1], categories, color="grey", size=11)
            ax.set_yticks([0.2, 0.4, 0.6, 0.8])
            ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8"], color="grey", size=9)
            plt.ylim(0, 1)
            
            # Add title with custom styling
            plt.title("Emotional Variation", pad=20, fontsize=16, fontweight='bold')
            
            # Add legend with better positioning and styling
            legend = plt.legend(
                loc='upper center', 
                bbox_to_anchor=(0.5, -0.05),
                ncol=3,
                frameon=True,
                facecolor='white',
                edgecolor='lightgrey'
            )
            
            plt.tight_layout()
            plt.savefig(f"{filename}-emotion_radar.png", dpi=300, bbox_inches="tight")
            chart_paths.append(f"{filename}-emotion_radar.png")
            plt.close()

    except Exception as e:
        print(f"Error generating emotion charts: {e}")

    return chart_paths

def format_text_for_pdf(text):
    """Convert markdown-style formatting to ReportLab HTML tags"""
    if not isinstance(text, str):
        return str(text)
    
    # Convert **bold** to <b>bold</b>
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Convert *italic* to <i>italic</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # Convert __underline__ to <u>underline</u>
    text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)
    
    # Clean up any remaining markdown artifacts
    text = text.replace('***', '').replace('~~~', '')
    
    return text

def generate_pdf_report(analysis_df, chart_paths,filename):
    """Generate comprehensive PDF report with enhanced UI"""
    #fstring for filename={filename}-ss



    # Enhanced page setup
    doc = SimpleDocTemplate(
        f"{filename}-journal_analysis_report.pdf",
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,
        bottomMargin=60,
    )

    # Enhanced color scheme
    colors_theme = {
        'primary': colors.HexColor("#2E5984"),
        'secondary': colors.HexColor("#4A90B8"), 
        'accent': colors.HexColor("#7BC3D1"),
        'text_dark': colors.HexColor("#2C3E50"),
        'text_light': colors.HexColor("#7F8C8D"),
        'background': colors.HexColor("#F8F9FA"),
        'success': colors.HexColor("#27AE60"),
        'warning': colors.HexColor("#F39C12"),
        'danger': colors.HexColor("#E74C3C")
    }

    # Get and enhance styles
    styles = getSampleStyleSheet()
    
    # Enhanced custom styles
    custom_styles = {
        'CustomTitle': ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=colors_theme['primary'],
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ),
        'CustomSubtitle': ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors_theme['secondary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ),
        'SectionHeader': ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors_theme['primary'],
            spaceBefore=25,
            spaceAfter=15,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=colors_theme['accent'],
            borderPadding=8,
            backColor=colors_theme['background']
        ),
        'SubSectionHeader': ParagraphStyle(
            'SubSectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors_theme['secondary'],
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            leftIndent=10,
            borderWidth=1,
            borderColor=colors_theme['accent'],
            borderPadding=4
        ),
        'EnhancedNormal': ParagraphStyle(
            'EnhancedNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors_theme['text_dark'],
            spaceBefore=6,
            spaceAfter=6,
            leading=16,
            leftIndent=15,
            fontName='Helvetica'
        ),
        'EnhancedBullet': ParagraphStyle(
            'EnhancedBullet',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors_theme['text_dark'],
            leftIndent=25,
            bulletIndent=15,
            spaceBefore=4,
            spaceAfter=4,
            bulletFontName='Helvetica-Bold',
            bulletFontSize=12,
            bulletColor=colors_theme['accent'],
            leading=14
        ),
        'EntryHeader': ParagraphStyle(
            'EntryHeader',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors_theme['primary'],
            spaceBefore=20,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            backColor=colors_theme['background'],
            borderWidth=1,
            borderColor=colors_theme['secondary'],
            borderPadding=6
        ),
        'DateStyle': ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors_theme['text_light'],
            spaceBefore=5,
            spaceAfter=5,
            alignment=TA_RIGHT,
            fontName='Helvetica-Oblique'
        ),
        'HighlightBox': ParagraphStyle(
            'HighlightBox',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors_theme['text_dark'],
            spaceBefore=10,
            spaceAfter=10,
            leftIndent=20,
            rightIndent=20,
            backColor=colors_theme['background'],
            borderWidth=1,
            borderColor=colors_theme['accent'],
            borderPadding=10,
            fontName='Helvetica'
        )
    }

    # Add custom styles to stylesheet
    for name, style in custom_styles.items():
        styles.add(style)

    elements = []

    # Enhanced Title Page with decorative elements
    
    # Add decorative header line
    header_line = Table([['']], colWidths=[7*inch])
    header_line.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors_theme['primary']),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(header_line)
    elements.append(Spacer(1, 20))
    
    # Main title with icon
    title = Paragraph("📋 <b>Psychological Journal Analysis Report</b>", styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 10))
    
    # Decorative separator
    separator = Table([['']], colWidths=[4*inch])
    separator.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors_theme['accent']),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(separator)
    elements.append(Spacer(1, 20))

    # Enhanced date range handling
    try:
        if "date" in analysis_df.columns and len(analysis_df) > 0:
            dates = pd.to_datetime(analysis_df["date"])
            date_min = dates.min().strftime("%B %d, %Y")
            date_max = dates.max().strftime("%B %d, %Y")
            if date_min == date_max:
                date_range = f"📅 {date_min}"
            else:
                date_range = f"📅 {date_min} to {date_max}"
        else:
            date_range = "📅 Analysis Period"
    except Exception as e:
        print(f"Error processing dates: {e}")
        date_range = "📅 Selected Period"

    subtitle = Paragraph(f"<i>{date_range}</i>", styles['CustomSubtitle'])
    elements.append(subtitle)
    
    # Add summary stats box
    stats_data = [
        ['📊 Total Entries', str(len(analysis_df))],
        ['📈 Analysis Type', 'Comprehensive Psychological Assessment'],
        ['🎯 Focus Areas', 'Emotions • Patterns • Insights • Recommendations']
    ]
    
    stats_table = Table(stats_data, colWidths=[2.5*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors_theme['background']),
        ('TEXTCOLOR', (0,0), (-1,-1), colors_theme['text_dark']),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors_theme['accent']),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors_theme['background'], colors.white])
    ]))
    
    elements.append(Spacer(1, 30))
    elements.append(stats_table)
    elements.append(Spacer(1, 40))

    # Executive Summary with enhanced layout
    elements.append(Paragraph("🎯 <b>Executive Summary</b>", styles['SectionHeader']))
    elements.append(Spacer(1, 15))

    # Generate comprehensive summary
    try:
        if "summary" in analysis_df.columns:
            all_summaries = "\n".join(analysis_df["summary"].astype(str))
        else:
            all_summaries = "No summary data available"

        summary_prompt = f"""Create a well-structured executive summary from these insights:
        {all_summaries}
        
        Return formatted with clear sections:
        ### Key Patterns
        - Bullet point 1
        - Bullet point 2
        
        ### Emotional Trends  
        - Bullet point 1
        - Bullet point 2
        
        ### Recommendations
        - Bullet point 1
        - Bullet point 2
        """

        executive_summary = analyze_with_llm_1(summary_prompt)
        
        # Process summary with enhanced formatting
        current_section = None
        for line in executive_summary.split("\n"):
            line = line.strip()
            if not line:
                continue

            if line.startswith("###"):
                section_title = line[3:].strip()
                # Add section icons
                if "Pattern" in section_title:
                    section_title = f"🔍 {section_title}"
                elif "Trend" in section_title:
                    section_title = f"📈 {section_title}"
                elif "Recommendation" in section_title:
                    section_title = f"💡 {section_title}"
                
                # Format the section title
                section_title = format_text_for_pdf(section_title)
                elements.append(Paragraph(section_title, styles['SubSectionHeader']))
                current_section = section_title
            elif line.startswith("-"):
                bullet_text = line[1:].strip()
                # Add contextual bullets
                if current_section and "Pattern" in current_section:
                    bullet_text = f"🔸 {bullet_text}"
                elif current_section and "Trend" in current_section:
                    bullet_text = f"📊 {bullet_text}"
                elif current_section and "Recommendation" in current_section:
                    bullet_text = f"✅ {bullet_text}"
                else:
                    bullet_text = f"• {bullet_text}"
                
                # Format the bullet text
                bullet_text = format_text_for_pdf(bullet_text)
                elements.append(Paragraph(bullet_text, styles['EnhancedBullet']))
            else:
                # Format regular text
                formatted_line = format_text_for_pdf(line)
                elements.append(Paragraph(formatted_line, styles['EnhancedNormal']))
                
    except Exception as e:
        print(f"Error generating summary: {e}")
        elements.append(Paragraph("⚠️ Summary analysis temporarily unavailable", styles['HighlightBox']))

    elements.append(Spacer(1, 30))

    # Enhanced Detailed Analysis Section
    elements.append(Paragraph("📝 <b>Detailed Entry Analysis</b>", styles['SectionHeader']))
    elements.append(Spacer(1, 15))

    if "title" in analysis_df.columns and "summary" in analysis_df.columns:
        for idx, (_, row) in enumerate(analysis_df.iterrows(), 1):
            # Enhanced date handling
            try:
                if hasattr(row["date"], 'strftime'):
                    date_str = row["date"].strftime("%A, %B %d, %Y")
                else:
                    date_str = str(row["date"])
            except:
                date_str = "Unknown date"

            # Entry header with numbering and enhanced styling
            entry_header = Paragraph(
                f"<b>Entry #{idx}: {row['title']}</b>", 
                styles['EntryHeader']
            )
            elements.append(entry_header)
            
            # Add date in smaller text
            date_paragraph = Paragraph(f"📅 {date_str}", styles['DateStyle'])
            elements.append(date_paragraph)
            elements.append(Spacer(1, 8))

            # Process summary with enhanced bullet points
            summary_text = str(row["summary"]) if pd.notna(row["summary"]) else ""
            for line_num, line in enumerate(summary_text.split("\n"), 1):
                line = line.strip()
                if line:
                    # Clean and enhance formatting
                    if line.startswith(("1.", "2.", "3.", "4.", "5.")):
                        line = line[2:].strip()
                        line = f"🔹 {line}"
                    elif line.startswith("*"):
                        line = line[1:].strip()
                        line = f"✦ {line}"
                    elif line.startswith("-"):
                        line = line[1:].strip()
                        line = f"▪️ {line}"
                    else:
                        line = f"• {line}"
                    
                    # Apply markdown-style formatting conversion
                    line = format_text_for_pdf(line)

                    # Now add the formatted line
                    elements.append(Paragraph(line, styles['EnhancedBullet']))


            elements.append(Spacer(1, 15))
            
            # Add separator between entries
            if idx < len(analysis_df):
                separator_line = Table([['']], colWidths=[6*inch])
                separator_line.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors_theme['accent']),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                elements.append(separator_line)
                elements.append(Spacer(1, 15))
    else:
        elements.append(
            Paragraph("⚠️ No detailed analysis data available", styles['HighlightBox'])
        )

    # Enhanced Visualizations Section
    if chart_paths:
        elements.append(PageBreak())
        elements.append(
            Paragraph("📊 <b>Psychological Trends Visualization</b>", styles['SectionHeader'])
        )
        elements.append(Spacer(1, 15))
        
        # Add intro text
        intro_text = Paragraph(
            "The following visualizations provide comprehensive insights into your emotional patterns, "
            "mood trends, and psychological states over the analyzed period.",
            styles['HighlightBox']
        )
        elements.append(intro_text)
        elements.append(Spacer(1, 20))

        chart_descriptions = {
            "mood_trend": {
                "title": "📈 Figure 1: Mood Fluctuation Trend Analysis",
                "desc": "This chart displays your emotional sentiment over time, helping identify patterns, peaks, and valleys in your overall mood state."
            },
            "emotional_composition": {
                "title": "🎭 Figure 2: Dominant Emotional States Distribution", 
                "desc": "A comprehensive breakdown of your primary emotional states, showing which emotions are most prevalent in your journal entries."
            },
            "emotion_radar": {
                "title": "🎯 Figure 3: Daily Emotional Variation Radar",
                "desc": "A radar chart showing the variation and intensity of different emotions across multiple days, revealing emotional consistency patterns."
            }
        }

        for idx, chart_path in enumerate(chart_paths, 1):
            chart_info = None
            for key, info in chart_descriptions.items():
                if key in chart_path:
                    chart_info = info
                    break
            
            if chart_info:
                # Chart title
                elements.append(Paragraph(chart_info["title"], styles['SubSectionHeader']))
                elements.append(Spacer(1, 8))
                
                # Chart description
                elements.append(Paragraph(chart_info["desc"], styles['EnhancedNormal']))
                elements.append(Spacer(1, 12))

            # Insert chart with enhanced styling
            try:
                # Create a frame around the image
                img_table = Table([[Image(chart_path, width=6*inch, height=4*inch)]], 
                                colWidths=[6.5*inch])
                img_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BACKGROUND', (0,0), (-1,-1), colors.white),
                    ('BOX', (0,0), (-1,-1), 2, colors_theme['secondary']),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                    ('LEFTPADDING', (0,0), (-1,-1), 10),
                    ('RIGHTPADDING', (0,0), (-1,-1), 10),
                ]))
                elements.append(img_table)
                elements.append(Spacer(1, 25))
                
            except Exception as e:
                print(f"Could not include image {chart_path}: {e}")
                elements.append(
                    Paragraph(f"⚠️ Chart visualization unavailable: {chart_path}", 
                             styles['HighlightBox'])
                )
                elements.append(Spacer(1, 15))

    # Enhanced Footer
    elements.append(PageBreak())
    
    # Add footer section
    footer_line = Table([['']], colWidths=[7*inch])
    footer_line.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors_theme['primary']),
    ]))
    elements.append(footer_line)
    elements.append(Spacer(1, 20))
    
    footer_text = Paragraph(
        "<b>📋 Report Generated Successfully</b><br/>"
        "This comprehensive psychological analysis provides insights into your emotional patterns and mental well-being. "
        "For questions about this analysis, consult with a qualified mental health professional.<br/><br/>"
        f"<i>Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
        styles['HighlightBox']
    )
    elements.append(footer_text)

    # Generate enhanced PDF
    doc.build(elements)
    return f"{filename}-journal_analysis_report.pdf"

def format_text_for_pdf(text):
    """Convert markdown-style formatting to ReportLab HTML tags"""
    if not isinstance(text, str):
        return str(text)
    
    # Convert **bold** to <b>bold</b>
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Convert *italic* to <i>italic</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # Convert __underline__ to <u>underline</u>
    text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)
    
    # Clean up any remaining markdown artifacts
    text = text.replace('***', '').replace('~~~', '')
    
    return text


def gen_mindlogpdf(authId,numdays,filename):
    """
    Main function to generate psychological journal analysis PDF report
    
    Args:
        authId (str): User authentication ID for Firestore query
        
    Returns:
        str: Path to generated PDF report
    """
    print("Journal Analysis Report Generator")
    print("--------------------------------")
    
    try:
        # Step 1: Retrieve journal entries from Firestore
        print("Step 1/4: Retrieving journal entries...")
        # Use the already initialized db from your setup
        
        journal_ref = db.collection("users").document(authId).collection("journalEntries")
        query = journal_ref.order_by("date", direction=firestore.Query.DESCENDING).limit(numdays)
        snapshot = query.stream()

        # Convert to DataFrame-compatible structure
        records = []
        for doc in snapshot:
            data = doc.to_dict()
            records.append({
                "entry_id": doc.id,
                "title": data.get("title", ""),
                "date": data.get("date"),
                "content": data.get("content", "")
            })

        if not records:
            print("No journal entries found for this user.")
            return None

        entries_df = pd.DataFrame(records)
        print(f"Retrieved {len(entries_df)} entries.")

        # Step 2: Analyze entries with LLM
        print("Step 2/4: Analyzing entries...")
        analysis_results = []
        
        for _, entry in entries_df.iterrows():
            # Comprehensive psychological analysis
            analysis_prompt = f"""
            Analyze this journal entry as a psychologist. Focus on key insights and actionable takeaways:

            Title: {entry['title']}
            Date: {entry['date']}
            Content: {entry['content']}

            Provide a concise yet comprehensive analysis covering:
            1. Emotional state (primary and secondary emotions)
            2. Cognitive patterns (positive/negative, rational/irrational)
            3. Stress indicators and coping mechanisms
            4. Notable behavioral patterns
            5. Key concerns or growth opportunities
            6. Specific recommendations for improvement

            Format your response with clear bullet points for each category.
            """
            analysis_text = analyze_with_llm_1(analysis_prompt)

            # Generate summary
            summary_prompt = f"""
            Summarize this psychological analysis into 1-2 key actionable insights from the journal entry:
            {analysis_text}

            Focus on the most important takeaways that the journal writer should pay attention to.
            Format as bullet points.
            """
            summary_text = analyze_with_llm_1(summary_prompt)

            # Emotion quantification
            emotion_prompt = f"""
            Analyze this journal entry and quantify the emotional content:
            {entry['content']}

            Return ONLY a JSON dictionary with values between 0-1 for these emotions: 
            {EMOTIONS}
            Example: {{"Joy": 0.5, "Sadness": 0.3, "Anger": 0.1, "Fear": 0.2, "Surprise": 0.0, "Disgust": 0.0, "Trust": 0.4, "Anticipation": 0.3}}
            """
            try:
                emotion_json = analyze_with_llm_1(
                    emotion_prompt,
                    system_prompt="You are an emotion analysis tool. Return ONLY valid JSON.",
                )
                # Clean the JSON response
                emotion_json_clean = emotion_json.strip().strip('`').replace('json\n', '').replace('json', '')
                emotion_data = json.loads(emotion_json_clean)
            except Exception as e:
                print(f"Error parsing emotion data: {e}")
                emotion_data = {e: 0 for e in EMOTIONS}

            analysis_results.append({
                "entry_id": entry["entry_id"],
                "date": entry["date"],
                "title": entry["title"],
                "content": entry["content"],
                "analysis": analysis_text,
                "summary": summary_text,
                "emotions": emotion_data,
            })

        analysis_df = pd.DataFrame(analysis_results)
        print("Analysis complete.")

        # Step 3: Generate visualizations
        print("Step 3/4: Generating visualizations...")
        chart_paths = generate_visualizations(analysis_df,filename)
        print(f"Created {len(chart_paths)} charts.")

        # Step 4: Generate PDF report
        print("Step 4/4: Generating PDF report...")
        report_path = generate_pdf_report(analysis_df, chart_paths,filename)
        print(f"\nReport successfully generated: {report_path}")
        
        return report_path

    except Exception as e:
        print(f"Error generating report: {e}")
        return None