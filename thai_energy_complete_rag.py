import pandas as pd
import gradio as gr
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import os
import json
from typing import List, Dict, Tuple

class ComprehensiveThaiEnergyRAG:
    def __init__(self, csv_file):
        """🇹🇭 ระบบ RAG ครอบคลุมสำหรับข้อมูลพลังงานไทยทั้งหมด 309 เอกสาร"""
        
        print("🇹🇭 กำลังโหลดระบบตอบคำถามพลังงานไทยแบบครอบคลุม...")
        print("📊 ใช้ข้อมูลทั้งหมด 309 เอกสารจากทุกหน่วยงาน")
        print("🏢 PEA, MEA, ERC, กระทรวงพลังงาน, EPPO")
        
        # โหลดข้อมูลทั้งหมด
        self.df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"✅ โหลดเอกสารทั้งหมด: {len(self.df)} ฉบับ")
        
        # แสดงสถิติตามองค์กร
        self.show_organization_stats()
        
        # โหลดโมเดล embedding (รองรับภาษาไทย)
        print("🤖 กำลังโหลดโมเดล AI หลายภาษา...")
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ โหลดโมเดล embedding สำเร็จ")
        
        # เตรียมเอกสารและสร้าง embeddings
        print("📄 กำลังเตรียมเอกสารทั้งหมด...")
        self.documents, self.metadata = self.prepare_all_documents()
        
        print("🔄 กำลังสร้าง embeddings สำหรับทุกเอกสาร...")
        self.embeddings = self.model.encode(self.documents, show_progress_bar=True)
        
        print("✅ ระบบ RAG ครอบคลุมพร้อมใช้งาน!")
        print(f"📚 จำนวนเอกสารที่ใช้งานได้: {len(self.documents)} ฉบับ")
    
    def show_organization_stats(self):
        """แสดงสถิติข้อมูลตามองค์กร"""
        print("\n📊 สถิติข้อมูลตามองค์กร:")
        print("=" * 50)
        
        org_counts = self.df.groupby('organization').size().sort_values(ascending=False)
        for org, count in org_counts.items():
            print(f"🏢 {org}: {count} เอกสาร")
        
        doc_type_counts = self.df.groupby('document_type').size().sort_values(ascending=False)
        print("\n📋 ประเภทเอกสาร:")
        for doc_type, count in doc_type_counts.items():
            print(f"📄 {doc_type}: {count} ฉบับ")
        print("=" * 50)
    
    def prepare_all_documents(self):
        """เตรียมเอกสารทั้งหมดสำหรับ embedding"""
        documents = []
        metadata = []
        
        print(f"📋 คอลัมน์ที่มี: {list(self.df.columns)}")
        
        successful_docs = 0
        for idx, row in self.df.iterrows():
            try:
                # ดึงข้อมูลจากแต่ละคอลัมน์
                org = self.safe_get(row, ['organization', 'org', 'source', 'องค์กร'])
                title = self.safe_get(row, ['title', 'name', 'subject', 'หัวข้อ', 'ชื่อ'])
                content = self.safe_get(row, ['content', 'text', 'body', 'description', 'เนื้อหา', 'รายละเอียด'])
                doc_type = self.safe_get(row, ['document_type', 'type', 'category', 'ประเภท'])
                url = self.safe_get(row, ['url', 'link', 'ลิงก์'])
                
                # สร้างข้อความเอกสารที่ครอบคลุม
                doc_parts = []
                if org:
                    doc_parts.append(f"องค์กร: {org}")
                if title:
                    doc_parts.append(f"หัวข้อ: {title}")
                if doc_type:
                    doc_parts.append(f"ประเภท: {doc_type}")
                if content:
                    # ทำความสะอาดเนื้อหา
                    clean_content = self.advanced_clean_content(content)
                    if clean_content:
                        doc_parts.append(f"เนื้อหา: {clean_content}")
                
                doc_text = "\n".join(doc_parts)
                
                # ตรวจสอบว่าเอกสารมีเนื้อหาเพียงพอ
                if len(doc_text.strip()) > 50:  # เพิ่มความเข้มงวด
                    documents.append(doc_text)
                    metadata.append({
                        'org': org,
                        'title': title,
                        'content': clean_content if content else "",
                        'type': doc_type,
                        'url': url,
                        'index': idx,
                        'full_text': doc_text
                    })
                    successful_docs += 1
                    
                    # แสดงตัวอย่างเอกสารแรก 5 ฉบับ
                    if successful_docs <= 5:
                        print(f"\n📄 เอกสารที่ {successful_docs}:")
                        print(f"  🏢 องค์กร: {org}")
                        print(f"  📝 หัวข้อ: {title[:80]}...")
                        print(f"  📋 ประเภท: {doc_type}")
                        print(f"  📊 ความยาว: {len(clean_content)} ตัวอักษร")
                
            except Exception as e:
                print(f"⚠️ ข้อผิดพลาดในเอกสารที่ {idx}: {e}")
                continue
            
            # แสดงความคืบหน้า
            if (idx + 1) % 50 == 0:
                print(f"⏳ ประมวลผลแล้ว: {idx + 1}/{len(self.df)} เอกสาร")
        
        print(f"✅ เตรียมเอกสารเรียบร้อย: {successful_docs}/{len(self.df)} ฉบับ")
        return documents, metadata
    
    def safe_get(self, row, possible_cols):
        """ดึงค่าจาก row อย่างปลอดภัย"""
        for col in possible_cols:
            for actual_col in row.index:
                if col.lower() in actual_col.lower():
                    val = row[actual_col]
                    return str(val).strip() if pd.notna(val) and str(val).strip() != 'nan' else ""
        return ""
    
    def advanced_clean_content(self, content):
        """ทำความสะอาดเนื้อหาขั้นสูง"""
        if pd.isna(content) or content == 'nan':
            return ""
        
        content = str(content)
        
        # ลบ HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # ลบอักขระพิเศษที่ไม่จำเป็น
        content = re.sub(r'[^\w\s\u0e00-\u0e7f.,!?;:()\-\'""/]', ' ', content)
        
        # ลบช่องว่างที่เกินไป
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n+', ' ', content)
        
        # ตัดให้เหมาะสม
        if len(content) > 1500:
            content = content[:1500] + "..."
        
        return content.strip()
    
    def intelligent_search(self, query, top_k=5):
        """ค้นหาแบบอัจฉริยะ"""
        
        # Encode คำถาม
        query_embedding = self.model.encode([query])
        
        # คำนวณความคล้าย
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # หาผลลัพธ์ที่ดีที่สุด
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'document': self.documents[idx],
                'metadata': self.metadata[idx],
                'similarity': similarities[idx]
            })
        
        return results
    
    def generate_comprehensive_answer(self, question):
        """สร้างคำตอบที่ครอบคลุม"""
        
        if not question.strip():
            return self.get_welcome_message()
        
        # ค้นหาเอกสารที่เกี่ยวข้อง
        results = self.intelligent_search(question, top_k=6)
        
        if not results or results[0]['similarity'] < 0.05:
            return self.get_no_results_message()
        
        # จัดกลุ่มผลลัพธ์ตามองค์กร
        org_results = {}
        for result in results:
            org = result['metadata']['org']
            if org not in org_results:
                org_results[org] = []
            org_results[org].append(result)
        
        # สร้างคำตอบที่ครอบคลุม
        response = "🇹🇭 **คำตอบจากระบบข้อมูลพลังงานไทย (309 เอกสาร)**\n\n"
        
        # ข้อมูลหลัก
        best_result = results[0]
        main_metadata = best_result['metadata']
        
        response += f"## 🎯 **ข้อมูลหลัก**\n"
        response += f"🏢 **{main_metadata['org']}**\n"
        response += f"📄 **{main_metadata['title']}**\n"
        response += f"📝 ประเภท: {main_metadata['type']}\n"
        response += f"🎯 ความเกี่ยวข้อง: {best_result['similarity']:.1%}\n\n"
        
        # เนื้อหาหลัก
        main_content = main_metadata['content']
        if len(main_content) > 1200:
            main_content = main_content[:1200] + "..."
        
        response += f"**📋 รายละเอียด:**\n{main_content}\n\n"
        
        # ข้อมูลจากองค์กรอื่น ๆ
        if len(org_results) > 1:
            response += "## 📚 **ข้อมูลเสริมจากหน่วยงานอื่น:**\n"
            
            count = 0
            for org, org_res in org_results.items():
                if org != main_metadata['org'] and count < 3:
                    best_org_result = org_res[0]
                    meta = best_org_result['metadata']
                    response += f"\n### 🏢 {org}\n"
                    response += f"📄 {meta['title'][:60]}...\n"
                    response += f"🎯 ความเกี่ยวข้อง: {best_org_result['similarity']:.1%}\n"
                    
                    if meta['content']:
                        short_content = meta['content'][:200] + "..." if len(meta['content']) > 200 else meta['content']
                        response += f"📝 {short_content}\n"
                    count += 1
        
        # สรุปครอบคลุม
        response += f"\n## 🔍 **สรุปการค้นหา:**\n"
        response += f"📊 พบข้อมูลที่เกี่ยวข้องจาก {len(org_results)} หน่วยงาน\n"
        response += f"📄 รวม {len(results)} เอกสาร\n"
        response += f"🎯 ความเกี่ยวข้องสูงสุด: {results[0]['similarity']:.1%}\n"
        
        # URL ถ้ามี
        if main_metadata['url'] and main_metadata['url'] != 'nan':
            response += f"\n🔗 **ลิงก์อ้างอิง:** {main_metadata['url']}"
        
        return response
    
    def get_welcome_message(self):
        """ข้อความต้อนรับ"""
        return """🇹🇭 **ยินดีต้อนรับสู่ระบบตอบคำถามพลังงานไทย**

📊 **ข้อมูลครอบคลุม 309 เอกสารจาก:**
🏢 PEA (การไฟฟ้าส่วนภูมิภาค)
🏢 MEA (การไฟฟ้านครหลวง) 
🏢 ERC (คณะกรรมการกำกับกิจการพลังงาน)
🏢 กระทรวงพลังงาน
🏢 EPPO (สำนักงานนโยบายและแผนพลังงาน)

🔍 **ลองถามคำถามเหล่านี้:**
• PEA มีนโยบายการจัดหาไฟฟ้าอย่างไร?
• ข้อมูลเกี่ยวกับมาตรฐานความปลอดภัยของ MEA
• การกำกับดูแลภาคพลังงานของ ERC
• นโยบายพลังงานของกระทรวงพลังงาน
• แผนพลังงานของ EPPO"""

    def get_no_results_message(self):
        """ข้อความเมื่อไม่พบผลลัพธ์"""
        return """🔍 **ไม่พบข้อมูลที่เกี่ยวข้องในฐานข้อมูล**

💡 **คำแนะนำ:**
• ลองใช้คำค้นที่เฉพาะเจาะจงมากขึ้น
• ระบุชื่อหน่วยงาน เช่น PEA, MEA, ERC
• ใช้คำภาษาไทยหรือภาษาอังกฤษ

🎯 **หัวข้อที่แนะนำ:**
• นโยบายพลังงาน • มาตรฐานความปลอดภัย
• การกำกับดูแล • แผนพลังงาน
• การจัดหาไฟฟ้า • ระเบียบและข้อบังคับ"""

def create_professional_demo_interface(rag_system):
    """สร้าง interface ระดับมืออาชีพสำหรับการ demo"""
    
    def chat_function(message, history):
        if not message.strip():
            return rag_system.get_welcome_message()
        
        try:
            response = rag_system.generate_comprehensive_answer(message)
            return response
        except Exception as e:
            return f"⚠️ เกิดข้อผิดพลาด: {str(e)}\n\nกรุณาลองใหม่อีกครั้ง"
    
    # สร้าง interface ระดับมืออาชีพ
    demo = gr.ChatInterface(
        fn=chat_function,
        title="🇹🇭 ระบบตอบคำถามพลังงานไทยแบบครอบคลุม | Comprehensive Thai Energy AI",
        description="""
        **🎯 ระบบ AI ตอบคำถามเกี่ยวกับข้อมูลพลังงานไทยที่ครอบคลุมที่สุด**
        
        📊 **ฐานข้อมูล:** 309 เอกสารจากหน่วยงานหลักทุกแห่ง  
        🏢 **ครอบคลุม:** PEA, MEA, ERC, กระทรวงพลังงาน, EPPO  
        🤖 **เทคโนโลยี:** AI หลายภาษา + Semantic Search  
        ⚡ **อัพเดท:** ข้อมูลล่าสุด ณ 28 กันยายน 2568  
        
        **Perfect for PEA Ambassador Presentations & Energy Sector Analysis**
        """,
        examples=[
            "PEA มีนโยบายการจัดหาไฟฟ้าและการกระจายพลังงานอย่างไร?",
            "ข้อมูลเกี่ยวกับมาตรฐานความปลอดภัยทางไฟฟ้าของ MEA",
            "การกำกับดูแลและควบคุมภาคพลังงานของ ERC",
            "นโยบายพลังงานและแผนยุทธศาสตร์ของกระทรวงพลังงาน",
            "แผนพัฒนาพลังงานและนโยบายของ EPPO",
            "What is PEA's electricity distribution and energy policy?",
            "MEA electrical safety standards and regulations",
            "ERC energy sector regulatory framework",
            "Thailand's national energy policy and strategy",
            "EPPO energy planning and development programs"
        ],
        theme=gr.themes.Soft(
            primary_hue="emerald",
            secondary_hue="blue", 
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Sarabun")
        ),
        css="""
        .gradio-container {
            font-family: 'Sarabun', 'Noto Sans Thai', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
        }
        .chat-message {
            font-size: 16px;
            line-height: 1.8;
            padding: 15px;
        }
        .message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .message.assistant {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .examples-container {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        """
    )
    
    return demo

# เริ่มต้นระบบครอบคลุม
if __name__ == "__main__":
    # ใช้ไฟล์ Complete Dataset ที่มี 309 เอกสารทั้งหมด
    csv_file = "Thai_Energy_Complete_Dataset_2025-09-28_12-16.csv"
    
    try:
        print("🇹🇭 เริ่มต้นระบบตอบคำถามพลังงานไทยแบบครอบคลุม...")
        print("📊 กำลังโหลดข้อมูลทั้งหมด 309 เอกสาร...")
        
        # ตรวจสอบไฟล์
        if not os.path.exists(csv_file):
            print(f"❌ ไม่พบไฟล์: {csv_file}")
            print("📂 ไฟล์ CSV ที่มีในโฟลเดอร์:")
            for file in os.listdir('.'):
                if file.endswith('.csv'):
                    print(f"  📄 {file}")
            exit()
        
        # สร้างระบบ RAG ครอบคลุม
        rag = ComprehensiveThaiEnergyRAG(csv_file)
        
        # ทดสอบระบบ
        test_questions = [
            "PEA มีนโยบายด้านพลังงานอะไรบ้าง?",
            "What does MEA do for electrical safety?",
            "ERC กำกับดูแลอย่างไร?",
            "นโยบายพลังงานของกระทรวงพลังงาน",
            "EPPO แผนพัฒนาพลังงาน"
        ]
        
        print("\n🧪 ทดสอบระบบด้วยคำถามตัวอย่าง:")
        for i, q in enumerate(test_questions[:2], 1):  # ทดสอบ 2 คำถามแรก
            print(f"\n--- การทดสอบที่ {i} ---")
            print(f"❓ คำถาม: {q}")
            answer = rag.generate_comprehensive_answer(q)
            print(f"✅ คำตอบ (150 ตัวอักษรแรก): {answer[:150]}...")
        
        # สร้าง demo interface ระดับมืออาชีพ
        demo = create_professional_demo_interface(rag)
        
        print(f"\n🚀 เริ่มต้นเซิร์ฟเวอร์ระดับมืออาชีพ...")
        print(f"🌐 ระบบจะเปิดที่: http://localhost:7860")
        print(f"🔗 Gradio จะสร้างลิงก์สาธารณะสำหรับการ demo")
        print(f"🎯 **พร้อมสำหรับการนำเสนอ PEA พรุ่งนี้!**")
        print(f"📊 รองรับข้อมูลครอบคลุมทั้งหมด 309 เอกสาร")
        
        # เปิด demo ระดับมืออาชีพ
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=True,  # สร้างลิงก์สาธารณะ
            show_error=True,
            favicon_path=None,
            app_kwargs={"title": "Thai Energy AI Assistant"}
        )
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        print("\n🔧 การแก้ไข:")
        print("1. ติดตั้ง packages:")
        print("   pip install sentence-transformers scikit-learn gradio pandas numpy")
        print("2. ตรวจสอบไฟล์ CSV")
        print("3. รันคำสั่ง: python thai_energy_complete_rag.py")
