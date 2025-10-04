import pandas as pd
import re
from typing import List, Tuple

def convert_thai_energy_csv_to_autotrain(input_file: str, output_file: str = "autotrain_data.csv"):
    """
    Convert your Thai Energy CSV to AutoTrain format
    Input: Thai_Energy_High_Priority_2025-09-28_12-16.csv
    Output: Ready-to-use AutoTrain CSV
    """
    
    print("🔄 Converting CSV to AutoTrain format...")
    
    # Read your CSV
    df = pd.read_csv(input_file)
    print(f"📊 Found {len(df)} documents")
    
    training_pairs = []
    
    for idx, row in df.iterrows():
        org = row.get('organization', 'Unknown')
        title = row.get('title', 'Untitled')
        content = row.get('content', '')
        doc_type = row.get('document_type', 'Document')
        
        # Clean content (remove excessive whitespace, truncate if too long)
        content = clean_content(content)
        
        # Generate Q&A pairs for each document
        pairs = generate_training_pairs(org, title, content, doc_type)
        training_pairs.extend(pairs)
        
        if (idx + 1) % 10 == 0:
            print(f"✅ Processed {idx + 1}/{len(df)} documents")
    
    # Create training DataFrame
    training_df = pd.DataFrame(training_pairs, columns=['text', 'target'])
    
    # Remove duplicates and empty entries
    training_df = training_df.drop_duplicates()
    training_df = training_df[training_df['text'].str.len() > 10]
    training_df = training_df[training_df['target'].str.len() > 20]
    
    # Save to CSV
    training_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✅ Conversion complete!")
    print(f"📄 Generated {len(training_df)} training pairs")
    print(f"💾 Saved to: {output_file}")
    print(f"📤 Ready to upload to Hugging Face!")
    
    return output_file

def clean_content(content: str) -> str:
    """Clean and truncate content for training"""
    if pd.isna(content):
        return ""
    
    # Remove excessive whitespace
    content = re.sub(r'\s+', ' ', str(content))
    
    # Truncate if too long (keep first 800 characters for context)
    if len(content) > 800:
        content = content[:800] + "..."
    
    return content.strip()

def generate_training_pairs(org: str, title: str, content: str, doc_type: str) -> List[Tuple[str, str]]:
    """Generate question-answer pairs from document data"""
    
    pairs = []
    
    if not content or len(content) < 20:
        return pairs
    
    # Basic organizational questions
    pairs.append((
        f"What does {org} say about {title}?",
        f"According to {org}, {content}"
    ))
    
    # Document type specific questions
    if doc_type.lower() == "policy":
        pairs.extend([
            (f"What is {org}'s policy on {title}?", f"{org}'s policy states: {content}"),
            (f"Explain {org}'s {title} policy", f"The policy document from {org} explains: {content}")
        ])
    
    elif doc_type.lower() == "standard":
        pairs.extend([
            (f"What are the standards for {title} at {org}?", f"The standards set by {org} include: {content}"),
            (f"Tell me about {org} standards for {title}", f"According to {org} standards: {content}")
        ])
    
    elif doc_type.lower() == "report":
        pairs.extend([
            (f"What does the {org} report say about {title}?", f"The {org} report indicates: {content}"),
            (f"Summarize the {title} report from {org}", f"The report from {org} shows: {content}")
        ])
    
    # Thai language questions (if content contains Thai)
    if any('\u0e00' <= char <= '\u0e7f' for char in content):
        pairs.extend([
            (f"{org} มีข้อมูลเกี่ยวกับ {title} หรือไม่?", f"ตามข้อมูลของ {org}: {content}"),
            (f"อธิบายเกี่ยวกับ {title} ของ {org}", f"จากเอกสารของ {org}: {content}")
        ])
    
    # General questions
    pairs.extend([
        (f"Tell me about {title}", f"Based on {org} documentation: {content}"),
        (f"What information does {org} provide about {title}?", f"{org} provides the following information: {content}"),
        (f"Can you explain {title} according to {org}?", f"According to {org}: {content}")
    ])
    
    # PEA-specific questions (if org is PEA)
    if "PEA" in org.upper():
        pairs.extend([
            (f"How does PEA handle {title}?", f"PEA's approach to {title}: {content}"),
            (f"What is PEA's position on {title}?", f"PEA's official position: {content}")
        ])
    
    return pairs

# Quick usage
if __name__ == "__main__":
    # Replace with your actual file path
    input_csv = "Thai_Energy_High_Priority_2025-09-28_12-16.csv"
    output_csv = "thai_energy_autotrain_ready.csv"
    
    try:
        convert_thai_energy_csv_to_autotrain(input_csv, output_csv)
        print("\n🎉 SUCCESS! Your data is ready for AutoTrain!")
        print(f"\n📋 Next steps:")
        print(f"1. Upload {output_csv} to HuggingFace")
        print(f"2. Start AutoTrain with meta-llama/Llama-3.2-1B-Instruct")
        print(f"3. Train for 2-3 epochs")
        print(f"4. Deploy to Spaces for demo!")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {input_csv}")
        print("Please make sure the file path is correct!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")