import openai
import anthropic
from typing import List, Dict, Optional, Any
from src.core.config import config_manager
import logging
import json
import requests
from src.core.video_processing import TextProcessor

class AIAnalyzer:
    def __init__(self):
        self.config = config_manager.get_ai_config()
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        
        # 根据配置初始化AI客户端
        if self.config.provider == "openai":
            self.client = openai.OpenAI(api_key=self.config.api_key)
        elif self.config.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
        elif self.config.provider == "deepseek":
            self.client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url="https://api.deepseek.com"
            )
        else:
            self.client = None
            self.logger.warning(f"不支持的AI提供者: {self.config.provider}")
    
    def extract_knowledge_points(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取知识点"""
        if not text.strip():
            return []
        
        # 将长文本分块处理
        segments = self.text_processor.segment_text(text, self.config.chunk_size)
        all_knowledge_points = []
        
        for segment in segments:
            knowledge_points = self._extract_knowledge_from_segment(segment)
            all_knowledge_points.extend(knowledge_points)
        
        return all_knowledge_points
    
    def _extract_knowledge_from_segment(self, text: str) -> List[Dict[str, Any]]:
        """从文本段中提取知识点"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                prompt = f"""
                请从以下文本中提取有价值的知识点，并以JSON格式返回。每个知识点应包含以下字段：
                - title: 知识点标题
                - content: 知识点详细内容
                - category: 知识分类（如：科技、生活、教育、娱乐等）
                - tags: 相关标签列表
                - importance: 重要性等级（1-5）

                文本内容：
                {text}

                请返回格式如下的JSON数组：
                [
                    {{
                        "title": "知识点标题",
                        "content": "知识点详细内容",
                        "category": "分类",
                        "tags": ["标签1", "标签2"],
                        "importance": 3
                    }}
                ]
                
                重要：只返回JSON，不要添加任何其他文字说明。
                """
                
                if self.config.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens,
                        response_format={"type": "json_object"}
                    )
                    
                    content = response.choices[0].message.content.strip()
                    
                    # 提取JSON部分（如果AI返回了额外的解释文本）
                    content = self._extract_json_from_response(content)
                    
                    knowledge_points = json.loads(content)
                    
                elif self.config.provider == "anthropic":
                    response = self.client.messages.create(
                        model=self.config.model,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        system="你是一个专业的知识提取助手，严格按照要求的JSON格式返回知识点，只返回JSON不要添加其他文字。",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    content = response.content[0].text.strip()
                    
                    # 提取JSON部分
                    content = self._extract_json_from_response(content)
                    
                    knowledge_points = json.loads(content)
                
                elif self.config.provider == "deepseek":
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens,
                        response_format={"type": "json_object"}
                    )
                    
                    content = response.choices[0].message.content.strip()
                    
                    # 提取JSON部分（如果AI返回了额外的解释文本）
                    content = self._extract_json_from_response(content)
                    
                    knowledge_points = json.loads(content)
                
                else:
                    # 本地模型或其他API
                    knowledge_points = self._call_local_model(prompt)
                
                # 确保返回的是列表
                if isinstance(knowledge_points, dict):
                    knowledge_points = [knowledge_points]
                elif not isinstance(knowledge_points, list):
                    knowledge_points = []
                
                return knowledge_points
                
            except openai.APIError as e:
                self.logger.error(f"AI API 错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return []
            except json.JSONDecodeError as e:
                self.logger.error(f"解析AI响应JSON失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return []
            except Exception as e:
                self.logger.error(f"AI分析失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return []
    
    def _extract_json_from_response(self, content: str) -> str:
        """从AI响应中提取JSON内容"""
        content = content.strip()
        
        # 尝试提取JSON部分
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        return content.strip()
    
    def _call_local_model(self, prompt: str) -> List[Dict[str, Any]]:
        """调用本地模型（如果配置了）"""
        # 这里可以集成本地的开源模型，如Ollama、vLLM等
        # 示例：调用Ollama API
        try:
            ollama_url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(ollama_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get('response', '')
            
            # 提取JSON部分
            content = self._extract_json_from_response(content)
            
            return json.loads(content)
        except Exception as e:
            self.logger.error(f"调用本地模型失败: {e}")
            return []
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """总结文本内容"""
        try:
            prompt = f"""
            请对以下文本进行简洁准确的总结，总结内容不超过{max_length}个字符：

            {text}
            """
            
            if self.config.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens // 4  # 总结通常不需要太多token
                )
                
                summary = response.choices[0].message.content.strip()
                
            elif self.config.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens // 4,
                    temperature=self.config.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                summary = response.content[0].text.strip()
            
            elif self.config.provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens // 4
                )
                
                summary = response.choices[0].message.content.strip()
            
            else:
                summary = self._call_local_model_summarize(prompt)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"内容总结失败: {e}")
            return ""
    
    def _call_local_model_summarize(self, prompt: str) -> str:
        """调用本地模型进行总结"""
        try:
            ollama_url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens // 4
                }
            }
            
            response = requests.post(ollama_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            self.logger.error(f"调用本地模型总结失败: {e}")
            return ""
    
    def classify_content(self, text: str) -> Dict[str, Any]:
        """内容分类和标签提取"""
        try:
            prompt = f"""
            请对以下文本进行分类和标签提取：
            1. 分类：从以下类别中选择最合适的（可多选）：科技、教育、生活、娱乐、财经、健康、体育、其他
            2. 标签：提取3-5个最相关的标签

            文本内容：
            {text}

            请返回如下格式的JSON：
            {{
                "category": "主要分类",
                "subcategories": ["子分类列表"],
                "tags": ["标签1", "标签2", "标签3"]
            }}
            """
            
            if self.config.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens // 3,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                classification = json.loads(content)
                
            elif self.config.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens // 3,
                    temperature=self.config.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                classification = json.loads(content)
            
            elif self.config.provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens // 3,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                classification = json.loads(content)
            
            else:
                classification = self._call_local_model_classify(prompt)
            
            return classification
            
        except Exception as e:
            self.logger.error(f"内容分类失败: {e}")
            return {"category": "其他", "subcategories": [], "tags": []}
    
    def _call_local_model_classify(self, prompt: str) -> Dict[str, Any]:
        """调用本地模型进行分类"""
        try:
            ollama_url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens // 3
                }
            }
            
            response = requests.post(ollama_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get('response', '')
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content)
        except Exception as e:
            self.logger.error(f"调用本地模型分类失败: {e}")
            return {"category": "其他", "subcategories": [], "tags": []}
    
    def generate_questions(self, text: str, num_questions: int = 3) -> List[str]:
        """基于文本生成问题"""
        try:
            prompt = f"""
            请基于以下文本生成{num_questions}个相关问题，问题应该有助于加深对内容的理解：

            {text}

            请返回问题列表，格式如下：
            ["问题1", "问题2", "问题3"]
            """
            
            if self.config.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens // 3,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                questions = json.loads(content)
                
            elif self.config.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens // 3,
                    temperature=self.config.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                questions = json.loads(content)
            
            elif self.config.provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens // 3,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                questions = json.loads(content)
            
            else:
                questions = self._call_local_model_generate_questions(prompt)
            
            # 确保返回的是列表
            if not isinstance(questions, list):
                questions = []
            
            return questions
            
        except Exception as e:
            self.logger.error(f"问题生成失败: {e}")
            return []

class KnowledgeRefiner:
    """知识精炼器 - 进一步处理AI提取的知识点"""
    
    @staticmethod
    def refine_knowledge(knowledge_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """精炼知识点，确保格式一致"""
        refined_knowledge = []
        
        for kp in knowledge_points:
            # 确保必需字段存在
            refined_kp = {
                "title": kp.get("title", "")[:100],  # 限制标题长度
                "content": kp.get("content", ""),
                "category": kp.get("category", "未分类"),
                "tags": kp.get("tags", []),
                "importance": min(max(kp.get("importance", 3), 1), 5)  # 确保重要性在1-5之间
            }
            
            # 清理标签，确保是字符串列表
            if not isinstance(refined_kp["tags"], list):
                refined_kp["tags"] = []
            
            refined_knowledge.append(refined_kp)
        
        return refined_knowledge

# 使用示例
def main():
    analyzer = AIAnalyzer()
    
    # 示例文本
    sample_text = """
    人工智能是计算机科学的一个分支，它试图理解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
    """
    
    # 提取知识点
    knowledge_points = analyzer.extract_knowledge_points(sample_text)
    print("提取的知识点:")
    for kp in knowledge_points:
        print(f"- {kp['title']}: {kp['content'][:50]}...")
    
    # 内容总结
    summary = analyzer.summarize_content(sample_text)
    print(f"\n内容总结: {summary}")
    
    # 内容分类
    classification = analyzer.classify_content(sample_text)
    print(f"\n内容分类: {classification}")
    
    # 生成问题
    questions = analyzer.generate_questions(sample_text)
    print(f"\n生成的问题: {questions}")

if __name__ == "__main__":
    main()