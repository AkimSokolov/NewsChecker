import os
from dotenv import load_dotenv

load_dotenv()


class MessageProcessor:


    def link_analysis(self, news_reliability_score, source_reliability_score, provoking_rate):
        if source_reliability_score == 2:
            return MessageProcessor.satirical()

        news_reliability_message = MessageProcessor.news_reliability(news_reliability_score)
        source_reliability_message = MessageProcessor.source_reliability(source_reliability_score)
        provoking_rate_message = MessageProcessor.provoking_rate(provoking_rate)
        fake_probability_message = MessageProcessor.fake_probability_message(news_reliability_score, source_reliability_score, provoking_rate)

        message_to_user = news_reliability_message + "\n" + source_reliability_message + "\n" + provoking_rate_message + "\n" + "\n" + fake_probability_message
        return message_to_user
    def text_analysis(self, news_reliability_score, provoking_rate):
        news_reliability_message = MessageProcessor.news_reliability(news_reliability_score)
        provoking_rate_message = MessageProcessor.provoking_rate(provoking_rate)
        fake_probability_message = MessageProcessor.fake_probability_message(news_reliability_score, 0.5, provoking_rate)

        message_to_user = news_reliability_message + "\n" + provoking_rate_message + "\n\n" + fake_probability_message
        return message_to_user
    def satirical():
        return os.getenv("COMPLETE_ANALYSIS_SATIRICAL")
    
    def news_reliability(score):
        text_score = str(round(score*100,1)) + "%"

        if score > 0.7:
            return os.getenv("COMPLETE_ANALYSIS_NEWS_RELIABILITY_GOOD").format(news_score=text_score)
        
        return os.getenv("COMPLETE_ANALYSIS_NEWS_RELIABILITY_BAD").format(news_score = text_score)
    
    
    def source_reliability(score):
        text_score = str(round(score*100,1))+"%"

        if score < 0.7:
            return os.getenv("COMPLETE_ANALYSIS_SOURCE_RELIABILITY_BAD").format(source_score = text_score)
        if score < 0.95:
            return os.getenv("COMPLETE_ANALYSIS_SOURCE_RELIABILITY_MODERATE").format(source_score=text_score)
        return os.getenv("COMPLETE_ANALYSIS_SOURCE_RELIABILITY_GOOD").format(source_score=text_score)
    
    
    def provoking_rate(score):
        text_score = str(round(score*100,1))+"%"

        if score < 0.2:
            return os.getenv("COMPLETE_ANALYSIS_PROVOKING_GOOD").format(provoking_score = text_score)
        if score < 0.6:
            return os.getenv("COMPLETE_ANALYSIS_PROVOKING_MODERATE").format(provoking_score=text_score)
        return os.getenv("COMPLETE_ANALYSIS_PROVOKING_BAD").format(provoking_score = text_score)
    
    
    def fake_probability_message(reliability_score, source_score, provoking_rate):
        if reliability_score < 0.7:
            if source_score >= 0.9:
                return os.getenv("COMPLETE_ANALYSIS_FINAL_MODERATE")
            return os.getenv("COMPLETE_ANALYSIS_FINAL_BAD")
        if provoking_rate > 0.8:
            return os.getenv("COMPLETE_ANALYSIS_FINAL_HIGH_PROVOKING")
        
        return os.getenv("COMPLETE_ANALYSIS_FINAL_GOOD")
        
        