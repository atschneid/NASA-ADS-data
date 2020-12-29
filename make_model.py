import gensim, gensim.models
import pickle
import numpy as np

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class RefCorpus:

    def __init__(self, input_path, include_ids=False):
        self.input_path = input_path
        self.include_ids = include_ids
        
    def __iter__(self):
        with open(self.input_path) as f:
            for line in f:
                if self.include_ids:
                    yield [line.split('\t')[0], eval( line.split('\t')[2] )]
                else:
                    yield eval( line.split('\t')[2] )

class RefModel:

    def __init__(self,corpus_path,sum_vecs=False):
        self.rc = RefCorpus(corpus_path)
        self.model = None
        self.sum_vecs = sum_vecs
        
    def train_model(self):
        self.model = gensim.models.Word2Vec(sentences=self.rc,size=25,window=1000,iter=5)

    def get_vecs(self,words,sum_vecs=None):
        wordvecs = [self.model.wv[word] for word in words if word in self.model.wv]
        if sum_vecs is None and self.sum_vecs or sum_vecs:
            wordvecs += [self.model.trainables.syn1neg[self.model.wv.vocab[word].index] for word in words if word in self.model.wv]
           
        if len(wordvecs) > 0:
            return np.average(wordvecs, axis=0)
        else:
            return None

    def save_vecs(self,lines,serialize=True,
                  save_file='ref_vecs',sum_vecs=None):
        outlines = []
        for line in lines:
            vec = self.get_vecs(line[1],sum_vecs)
            if vec is not None:
                outlines += [[line[0], vec]]

        if serialize:
            with open(save_file + '.pk', 'wb') as f:
                pickle.dump(outlines, f)
        else:
            with open(save_file + '.tsv', 'w') as f:
                f.write('\n'.join( ['{}\t{}'.format(*line) for line in outlines] ))

    def save_model(self,save_file):
        self.model.save(save_file)

if __name__ == "__main__":
    print( 'gensim {}'.format(gensim.__version__) )
    rm = RefModel('refs_data.tsv')
    rm.train_model()
    rc = RefCorpus('refs_data.tsv', include_ids=True)
    rm.save_vecs(rc, save_file='ref_vecs_word_25d', sum_vecs=False)
    rm.save_vecs(rc, save_file='ref_vecs_ctxt_25d', sum_vecs=True)

