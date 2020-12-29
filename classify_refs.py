import sys, os
import sklearn
import numpy as np
from numpy import dot
from numpy.linalg import norm
import pickle
from sklearn.neighbors import KNeighborsClassifier

class BOWVectorizer:

    def __init__(self, vocab):
        self.n = len(vocab)
        self.lookup = {w : n for n,w in enumerate(vocab)}
        self.bids = {}

    def get(self, bid):
        if bid in self.bids:
            return self.bids[bid]

    def get_mean(self, bids):
        return np.mean([self.bids[bid] for bid in bids], axis=0)

    def add_bid(self,bid,terms):
        vec = np.zeros(self.n)
        for t in terms:
            vec[self.lookup[t]] += 1
        self.bids[bid] = vec

    
data_file = sys.argv[1]
vec_file = sys.argv[2]

def knn_classify_test(data_file,vec_path,knn_neighbors=5):

    # Check if vec_path is a directory or a single file
    try:
        with open(vec_path) as f:
            pass            
        vec_files = [vec_path]
    except IsADirectoryError:
        vec_files = [os.path.join(vec_path,f) for f in os.listdir(vec_path) if f.split('.')[-1] == '.pk']

    years = {}
    keywords = set()
    # We parse the data file once to get all keywords, all year values
    with open(data_file) as f:
        for line in f:
            year = int(line.strip().split('\t')[-1])
            years[year] = years.get(year,0) + 1

            kw = eval(line.strip().split('\t')[1])
            keywords |= kw

    year_cutoff = sorted(list(years.keys()))[-2]
    # print(years, sorted(list(years.keys())), year_cutoff)

    vectorizer = BOWVectorizer(keywords)

    train_ids = []
    test_ids = []
    used_ids = set()
    count_doubles = 0
    with open(data_file) as f:
        for line in f:
            fields = line.strip().split('\t')
            bid = fields[0]
            kws = eval(fields[1])
            year = int(fields[-1])

            if bid not in used_ids:
                if year < year_cutoff:
                    train_ids += [bid]
                else:
                    test_ids += [bid]
                used_ids.add(bid)

                vectorizer.add_bid(bid,kws)
            else:
                # print('double id : {}'.format(bid))
                count_doubles += 1

    print('count ids : {}, doubles : {}'.format(len(used_ids),count_doubles))

    for vec_file in vec_files:

        vec_array = pickle.load( open(vec_file, 'rb') )
        vectors = {v[0] : v[1] for v in vec_array}

        knn = KNeighborsClassifier(n_neighbors=knn_neighbors)

        train_y = [bid for bid in train_ids if bid in vectors]
        train_X = [vectors[bid] for bid in train_y]

        test_y = [bid for bid in test_ids if bid in vectors]
        test_X = [vectors[bid] for bid in test_y]

        print( 'train values : {}, test values : {}'.format(len(train_y), len(test_y)) )
        print( 'fitting knn...' )
        knn.fit(train_X,train_y)

        print( 'predicting knn...' )
        pred_probs = knn.predict_proba( test_X )

        print( 'generating vectors...' )
        preds = [vectorizer.get_mean(knn.classes_[pp.astype(np.bool)]) for pp in pred_probs]
        trues = [vectorizer.get(test_y[n]) for n in range(len(pred_probs))]

        print( 'normalizing...' )
        preds = [vec / norm(vec) for vec in preds]
        trues = [vec / norm(vec) for vec in trues]

        avg_cosine = np.mean( np.sum( np.array(trues) * np.array(preds), axis=1 ) )

        print( '{} cosine : {}'.format(vec_file, avg_cosine) )

if __name__ == "__main__":
    data_file = sys.argv[1]
    vec_file = sys.argv[2]
    knn_classify_test(data_file,vec_file)


