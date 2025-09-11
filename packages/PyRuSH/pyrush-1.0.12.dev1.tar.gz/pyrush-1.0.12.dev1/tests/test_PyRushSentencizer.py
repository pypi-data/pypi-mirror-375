import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyRuSH import PyRuSHSentencizer
from spacy.lang.en import English


class TestRuSH(unittest.TestCase):

    def setUp(self):
        self.pwd = os.path.dirname(os.path.abspath(__file__))

    def test_doc(self):
        nlp = English()
        nlp.add_pipe("medspacy_pyrush")
        doc = nlp("This is a sentence. This is another sentence.")
        print('\n'.join([str(s) for s in doc.sents]))
        print('\nTotal sentences: {}'.format(len([s for s in doc.sents])))
        print('\ndoc is an instance of {}'.format(type(doc)))

    def test_doc2(self):
        input_str = '''        

        
        Ms. ABCD is a 69-year-old lady, who was admitted to the hospital with chest pain and respiratory insufficiency.  She has chronic lung disease with bronchospastic angina.
We discovered new T-wave abnormalities on her EKG.  There was of course a four-vessel bypass surgery in 2001.  We did a coronary angiogram.  This demonstrated patent vein grafts and patent internal mammary vessel and so there was no obvious new disease.
She may continue in the future to have angina and she will have nitroglycerin available for that if needed.
Her blood pressure has been elevated and so instead of metoprolol, we have started her on Coreg 6.25 mg b.i.d.  This should be increased up to 25 mg b.i.d. as preferred antihypertensive in this lady's case.  She also is on an ACE inhibitor.
So her discharge meds are as follows:
1.  Coreg 6.25 mg b.i.d.
2.  Simvastatin 40 mg nightly.
3.  Lisinopril 5 mg b.i.d.
4.  Protonix 40 mg a.m.
5.  Aspirin 160 mg a day.
6.  Lasix 20 mg b.i.d.
7.  Spiriva puff daily.
8.  Albuterol p.r.n. q.i.d.
9.  Advair 500/50 puff b.i.d.
10.  Xopenex q.i.d. and p.r.n.
I will see her in a month to six weeks.  She is to follow up with Dr. X before that.
        


 Ezoic - MTSam Sample Bottom Matched Content - native_bottom 




 End Ezoic - MTSam Sample Bottom Matched Content - native_bottom
'''
        nlp = English()
        nlp.add_pipe("medspacy_pyrush", config={"rules_path": os.path.join(self.pwd, 'rush_rules.tsv')})
        doc = nlp(input_str)
        sents = [s for s in doc.sents]
        for sent in sents:
            print('>' + str(sent) + '<\n\n')

        # New expected count includes whitespace-only sentences
        assert (len(sents) == 51)
        # For content checks, filter out whitespace-only sentences
        content_sents = [s for s in sents if s.text.strip()]
        assert (content_sents[0].text == 'Ms. ABCD is a 69-year-old lady, who was admitted to the hospital with chest pain and respiratory insufficiency.')

    def test_doc3(self):
        input_str = '''        


            Ms. ABCD is a 69-year-old lady, who was admitted to the hospital with chest pain and respiratory insufficiency.  She has chronic lung disease with bronchospastic angina.
    We discovered new T-wave abnormalities on her EKG.  There was of course a four-vessel bypass surgery in 2001.  We did a coronary angiogram. 
    
    '''
        from loguru import logger
        logger.add(sys.stdout, level="DEBUG")
        nlp = English()
        nlp.add_pipe("medspacy_pyrush", config={"rules_path": os.path.join(self.pwd, 'rush_rules.tsv')})
        doc = nlp(input_str)
        sents = [s for s in doc.sents]
        for sent in sents:
            logger.debug('>' + str(sent) + '<\n\n')

        # SpaCy has no control of sentence end. Thus, it ends up with sloppy ends.
        assert (sents[1].text == 'Ms. ABCD is a 69-year-old lady, who was admitted to the hospital with'
                                     ' chest pain and respiratory insufficiency.')

    def test_customized_rules(self):
        input_str = '''        


            Ms. ABCD is a 69-year-old lady, who was admitted to the hospital with chest pain and respiratory insufficiency.  She has chronic lung disease with bronchospastic angina.
    We discovered new T-wave abnormalities on her EKG.  There was of course a four-vessel bypass surgery in 2001.  We did a coronary angiogram. 

    '''
        from loguru import logger
        logger.add(sys.stdout, level="DEBUG")
        from PyRuSH import RuSH
        pwd = os.path.dirname(os.path.abspath(__file__))
        rush = RuSH(str(os.path.join(pwd, 'rush_rules.tsv')), enable_logger=True)
        sentences = rush.segToSentenceSpans(input_str)
        # for i in range(0, len(sentences)):
        #     sentence = sentences[i]
        #     logger.debug('assert (sentences[' + str(i) + '].begin == ' + str(sentence.begin) + ' and sentences[' + str(
        #         i) + '].end == ' + str(sentence.end + ')')
        # self.printDetails(sentences, input_str)
        # logger.debug('\n\n'.join(['>{}<'.format(input_str[s.begin:s.end]) for s in sentences]))


        nlp = English()
        rule_path=os.path.join(os.path.dirname(__file__), 'rush_rules.tsv')
        nlp.add_pipe("medspacy_pyrush", config={'rules_path':rule_path})
        doc = nlp(input_str)
        sents = [s for s in doc.sents]
        for sent in sents:
            logger.debug('>' + str(sent) + '<\n\n')

        # SpaCy has no control of sentence end. Thus, it ends up with sloppy ends.
        assert (sents[1].text == 'Ms. ABCD is a 69-year-old lady, who was admitted to the hospital with'
                                 ' chest pain and respiratory insufficiency.')
                