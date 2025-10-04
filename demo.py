"""
Thai Energy RAG System - Perfect for PEA Demo Tomorrow!
Fetches content dynamically from URLs using your scraped metadata
"""

import pandas as pd
import gradio as gr
import requests
from bs4 import BeautifulSoup
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from typing import List, Dict, Tuple
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThaiEnergyRAG:
    def __init__(self, csv_file: str):
        print("🚀 Loading Thai Energy RAG System...")
        print("=" * 60)
        
        # Load metadata
        self.df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"📊 Loaded {len(self.df)} documents")
        
        # Initialize embedding model
        print("🤖 Loading multilingual embedding model...")
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # Prepare document metadata
        self.documents = self.prepare_documents()
        
        # Create embeddings
        print("🔄 Creating metadata embeddings...")
        self.embeddings = self.model.encode(self.documents)
        
        # Cache for fetched content
        self.content_cache = {}
        
        print("✅ Thai Energy RAG System Ready!")
        print("🎯 Perfect for PEA Demo Tomorrow!")
        print("=" * 60)
    
    def prepare_documents(self) -> List[str]:
        documents = []
        for _, row in self.df.iterrows():
            title = str(row.get('Document_Title_Thai', 'Unknown'))
            source = str(row.get('Source', 'Unknown'))
            doc_type = str(row.get('Document_Type', 'Document'))
            doc_text = f"{source}: {title} ({doc_type})"
            documents.append(doc_text)
        return documents
    
    def fetch_content_from_url(self, url: str) -> str:
        if url in self.content_cache:
            return self.content_cache[url]
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                if len(text) > 2000:
                    text = text[:2000] + "..."
                
                self.content_cache[url] = text
                return text
            else:
                return "ไม่สามารถดึงข้อมูลจากไฟล์ PDF หรือเอกสารประเภทนี้ได้"
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return f"ไม่สามารถดึงข้อมูลจาก URL นี้ได้"
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        query_embedding = self.model.encode([query])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            row_data = self.df.iloc[idx]
            results.append({
                'index': idx,
                'similarity': similarities[idx],
                'title': row_data.get('Document_Title_Thai', 'Unknown'),
                'source': row_data.get('Source', 'Unknown'),
                'doc_type': row_data.get('Document_Type', 'Document'),
                'url': row_data.get('Document_URL', ''),
                'metadata': self.documents[idx]
            })
        
        return results
    
    def answer_question(self, question: str) -> str:
        print(f"🔍 Processing question: {question}")
        
        results = self.search_documents(question, top_k=3)
        
        if not results or results[0]['similarity'] < 0.1:
            return self.create_fallback_response(question)
        
        response_parts = []
        response_parts.append("ตามข้อมูลจากฐานข้อมูลพลังงานไทย:\n")
        
        for i, result in enumerate(results[:2], 1):
            title = result['title']
            source = result['source']
            doc_type = result['doc_type']
            url = result['url']
            similarity = result['similarity']
            
            response_parts.append(f"\n📄 แหล่งข้อมูลที่ {i}: {source}")
            response_parts.append(f"📋 เรื่อง: {title}")
            response_parts.append(f"📝 ประเภท: {doc_type}")
            
            if url and url != 'nan':
                print(f"📡 Fetching content from: {url}")
                content = self.fetch_content_from_url(url)
                if content and len(content) > 50:
                    response_parts.append(f"📖 ข้อมูล: {content[:300]}...")
                else:
                    response_parts.append("📖 ข้อมูล: ไม่สามารถดึงเนื้อหาได้ในขณะนี้")
            
            response_parts.append(f"🎯 ความเกี่ยวข้อง: {similarity:.1%}")
            response_parts.append(f"🔗 ลิงก์: {url}\n")
        
        response_parts.append("\n💡 หมายเหตุ: ข้อมูลนี้ดึงมาจากเว็บไซต์ราชการโดยตรง")
        
        return "\n".join(response_parts)
    
    def create_fallback_response(self, question: str) -> str:
        question_lower = question.lower()
        
        if 'pea' in question_lower or 'การไฟฟ้าส่วนภูมิภาค' in question_lower:
            pea_docs = self.df[self.df['Source'] == 'PEA']
            if len(pea_docs) > 0:
                sample_doc = pea_docs.iloc[0]
                return f"""🔍 ไม่พบข้อมูลที่ตรงกับคำถามโดยตรง แต่เรามีข้อมูลเกี่ยวกับ PEA:

📄 ตัวอย่างเอกสาร: {sample_doc.get('Document_Title_Thai', 'Unknown')}
🏢 หน่วยงาน: การไฟฟ้าส่วนภูมิภาค (PEA)
📝 ประเภท: {sample_doc.get('Document_Type', 'Document')}

💡 ลองถามคำถามที่เฉพาะเจาะจงมากขึ้น เช่น:
- PEA มีนโยบายอะไรเกี่ยวกับพลังงานหมุนเวียน?
- ขั้นตอนการขอใช้ไฟฟ้าจาก PEA?
- มาตรฐานการให้บริการของ PEA?"""

        elif 'mea' in question_lower or 'การไฟฟ้านครหลวง' in question_lower:
            mea_docs = self.df[self.df['Source'] == 'MEA']
            if len(mea_docs) > 0:
                sample_doc = mea_docs.iloc[0]
                return f"""🔍 ไม่พบข้อมูลที่ตรงกับคำถามโดยตรง แต่เรามีข้อมูลเกี่ยวกับ MEA:

📄 ตัวอย่างเอกสาร: {sample_doc.get('Document_Title_Thai', 'Unknown')}
🏢 หน่วยงาน: การไฟฟ้านครหลวง (MEA)
📝 ประเภท: {sample_doc.get('Document_Type', 'Document')}

💡 ลองถามคำถามที่เฉพาะเจาะจงมากขึ้น เช่น:
- MEA มีบริการอะไรบ้าง?
- นโยบายของ MEA เกี่ยวกับความปลอดภัย?
- ขั้นตอนการขอใช้ไฟฟ้าจาก MEA?"""
        
        return """🔍 ขออภัย ไม่พบข้อมูลที่เกี่ยวข้องโดยตรงในฐานข้อมูล

📚 เรามีข้อมูลจาก:
• การไฟฟ้าส่วนภูมิภาค (PEA) - 114 เอกสาร
• การไฟฟ้านครหลวง (MEA) - 82 เอกสาร  
• คณะกรรมการกำกับกิจการพลังงาน (ERC) - 69 เอกสาร
• สำนักงานนโยบายและแผนพลังงาน (EPPO) - 44 เอกสาร

💡 ลองถามคำถามเกี่ยวกับ:
- นโยบายด้านพลังงาน
- ขั้นตอนการขอใช้ไฟฟ้า
- มาตรฐานความปลอดภัย
- พลังงานหมุนเวียน"""


def create_demo_interface(rag_system):
    def chat_function(message, history):
        try:
            response = rag_system.answer_question(message)
            return response
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"
    
    demo = gr.ChatInterface(
        fn=chat_function,
        title="🇹🇭 Thai Energy Knowledge Assistant - PEA Demo",
        description="""
**ระบบตอบคำถามเกี่ยวกับข้อมูลพลังงานไทย**

✨ **ความสามารถ:**
- ตอบคำถามเกี่ยวกับ PEA, MEA, ERC, EPPO
- ดึงข้อมูลจากเว็บไซต์ราชการโดยตรง  
- รองรับภาษาไทยและอังกฤษ
- แสดงแหล่งที่มาและลิงก์เอกสาร

🚀 **พร้อมสำหรับการนำเสนอ PEA พรุ่งนี้!**
        """,
        examples=[
            "What is PEA's electricity policy?",
            "PEA มีนโยบายการจัดหาไฟฟ้าอย่างไร?",
            "Tell me about MEA's electrical safety standards",
            "ข้อมูลเกี่ยวกับมาตรฐานความปลอดภัยของ MEA",
            "How does ERC regulate the energy sector?",
            "การกำกับดูแลภาคพลังงานของ กกพ.",
            "ขั้นตอนการขอใช้ไฟฟ้าจาก PEA",
            "MEA มีบริการอะไรบ้าง?"
        ],
        theme=gr.themes.Soft()
    )
    
    return demo


if __name__ == "__main__":
    CSV_FILE = "Thai_Energy_High_Priority_2025-09-28_12-16.csv"
    
    try:
        print("🇹🇭 THAI ENERGY RAG SYSTEM")
        print("=" * 60)
        print("🎯 Ready for PEA Demo Tomorrow!")
        print("=" * 60)
        
        # Create RAG system
        rag = ThaiEnergyRAG(CSV_FILE)
        
        # Test the system
        print("\n🧪 Testing the system...")
        test_question = "What does PEA say about electricity distribution?"
        print(f"\n❓ Test: {test_question}")
        answer = rag.answer_question(test_question)
        print(f"✅ Response: {answer[:200]}...")
        
        # Create and launch demo
        print(f"\n🚀 Starting Thai Energy Demo Server...")
        print(f"🌐 Perfect for PEA Presentation Tomorrow!")
        
        demo = create_demo_interface(rag)
        
        # Launch with public sharing for demo
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=True,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📋 Install required packages:")
        print("pip install -r requirements.txt")
