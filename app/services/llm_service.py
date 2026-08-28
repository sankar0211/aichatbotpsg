import os
from groq import Groq
from app.services.rag_service import rag_service
from app.models import ChatMessage, ChatSession
from app import db

class LLMService:
    def __init__(self):
        # We use a fast, free LLM hosted on Groq
        self.model_name = os.getenv('LLM_MODEL', 'llama-3.1-8b-instant')
        api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=api_key) if api_key else None

    def generate_response_stream(self, session_id: int, user_message: str):
        try:
            if not self.client:
                yield " Error: GROQ_API_KEY is not set in the environment variables. Please add it to your .env file."
                return

            # 1. Retrieve Context
            faq_match = rag_service.search(user_message)
            if faq_match:
                context = f"You are an AI assistant for PSG College of Technology. Use this information to answer naturally:\n{faq_match}"
            else:
                context = "You are an AI assistant for PSG College of Technology. Answer naturally based on your general knowledge."

            # 2. Get Chat History
            history = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.desc()).limit(5).all()
            history.reverse()

            messages = [{"role": "system", "content": context}]
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": user_message})

            # 3. Save User Message
            user_msg_record = ChatMessage(session_id=session_id, role='user', content=user_message)
            db.session.add(user_msg_record)
            db.session.commit()

            # 4. Generate Response (Streaming via Groq)
            bot_reply_full = ""
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    bot_reply_full += content
                    yield content
                
            # 5. Save Bot Response
            if bot_reply_full:
                bot_msg_record = ChatMessage(session_id=session_id, role='bot', content=bot_reply_full)
                db.session.add(bot_msg_record)
                db.session.commit()

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in stream: {error_details}")
            yield f" \n\n**System Error:** Could not process request.\n```\n{e}\n```"

llm_service = LLMService()
