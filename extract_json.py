import sys
import os
import json
import pickle

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Extract:
    """This is a class for extracting information from ADS downloads

    Methods for various goals of analysis.
    """
    
    def __init__(self, source, target_name='abstract_text.tsv'):
        self.source = source
        self.save_file = target_name
        self.orcid_dict = {}
        self.orcid_count = 0
        self.output_lines = []

        try:
            with open(source) as f:
                pass            
            self.source_files = [source]
        except IsADirectoryError:
            self.source_files = [os.path.join(self.source,f) for f in os.listdir(self.source)]

        
    def get_firstauthors_text(self, first_only=True):
        """Generates a list of Author_id \t Title \t Abstract Text using Orcid

        This method creates numeric alias (Author_id) for unique OrcIDs, then generates a 
        list of strings of the form Author_id \t Title \t Abstract Text.

        This method searches in the following order: orcid_pub, orcid_user, orcid_other
        If no first author OrcID data is present, the article is skipped.
        """
        
        art_count = 0
        art_w_orc = 0
        for fname in self.source_files:
            with open(fname) as f:
                content = json.load(f)
                for doc in content['response']['docs']:
                    art_count += 1
                    if 'orcid_pub' in doc and \
                       doc['orcid_pub'][0] != '-':
                        orcs = doc['orcid_pub']
                    elif 'orcid_user' in doc and \
                         doc['orcid_user'][0] != '-':
                        orcs = doc['orcid_user']
                    elif 'orcid_other' in doc and \
                         doc['orcid_other'][0] != '-':
                        orcs = doc['orcid_other']
                    else:
                        continue

                    for orcid in orcs:
                        if orcid not in self.orcid_dict:
                            self.orcid_dict[orcid] = self.orcid_count
                            self.orcid_count += 1
                        if first_only:
                            break
                    orcid = self.orcid_dict[orcs[0]]

                    if 'abstract' not in doc:
                        continue
                    abstract = doc['abstract'].replace('\t', ' ')

                    if 'title' not in doc:
                        title = ' '
                    else:                        
                        title = doc['title'][0].replace('\t', ' ').replace('\n', ' ')

                    self.output_lines += ['{}\t{}\t{}'.format(orcid,title,abstract)]

                    art_w_orc += 1
        print('count orcids : {}, total articles : {}, valid articles : {}'.format(len(self.orcid_dict), art_count, art_w_orc))

    def get_keyword_refs(self, min_count=1000):
        """Generates a list of strings formatted: Bibcode_id \t [keywords] \t [references] 

        This method keeps keywords occurring at least `min_count` times (default: 1000). Articles containing no valid keywords are skipped.
        """
        
        art_count = 0
        keep_art_ct = 0
        keys = set()
        keywords = {}
        for fname in self.source_files:
            with open(fname) as f:
                content = json.load(f)
                for doc in content['response']['docs']:
                    art_count += 1
                    keys |= set(doc.keys())
                    for kw in doc['keyword_norm']:
                        keywords[kw] = keywords.get(kw,0) + 1
                    # self.output_lines += ['{}\t{}\t{}'.format(orcid,title,abstract)]

        keep_keys = set([k for k in keywords if keywords[k] > min_count]) - {'-'}
        print('total articles : {}, number keywords : {}'.format(art_count, len(keep_keys)))
        for fname in self.source_files:
            with open(fname) as f:
                content = json.load(f)
                for doc in content['response']['docs']:
                    kws = keep_keys & set(doc['keyword_norm'])
                    for kw in kws:
                        if kw in keep_keys and 'reference' in doc:
                            refs = doc['reference']
                            bid = doc['bibcode']
                            year = doc['year']
                            
                            self.output_lines += [[bid,kws,refs,year]]
                            keep_art_ct += 1
                            break

        print('keeping articles : {}'.format(keep_art_ct))
        
        
    def write_file(self, save_file=None, serialize=False):
        """Commits the list of strings output_lines to file"""
        if save_file is None:
            save_file = self.save_file
            
        if serialize:
            with open(save_file, 'wb') as f:
                pickle.dump(self.output_lines, f)
        else:
            with open(save_file, 'w') as f:
                f.write('\n'.join(['{}\t{}\t{}\t{}'.format(*line) for line in self.output_lines]))

if __name__ == "__main__":
    if len(sys.argv) == 3:
        in_file = sys.argv[1]
        outfile = sys.argv[2]

        ext = Extract(in_file)
        ext.get_keyword_refs()

        ext.write_file(outfile,serialize=False)
    else:
        ext = Extract('ref_data')
        ext.get_keyword_refs()
        # ext.get_firstauthors_text()
        ext.write_file('refs_data.pk',serialize=True)
        ext.write_file('refs_data.tsv',serialize=False)
