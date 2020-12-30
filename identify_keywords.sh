token="<your ADS token here; `see https://github.com/adsabs/adsabs-dev-api#access`>"
filename=cosmology

if [ ! -d ${filename}_data ]; then
    mkdir ${filename}_data
fi

# add search terms here
for keyword in %22Cosmology%22; do

    # ADS limits search rows per query, so run a bunch of queries successively
    for i in {0..100}; do

	curl -H "Authorization: Bearer $token" \
	     "https://api.adsabs.harvard.edu/v1/search/query?q=keyword:${keyword}&fq=year:2000-&fl=bibcode,title,keyword_norm,year,reference&rows=100&start=${i}00" \
	     > ${filename}_data/ADSdata_${keyword}_${i}

	echo ${i}00
    done
done

python extract_json.py ${filename}_data ${filename}_data.tsv

if [ ! -d vectors ]; then
    mkdir vectors
fi

python make_model.py ${filename}_data.tsv vectors/${filename}_vecs

python classify_refs.py ${filename}_data.tsv vectors/
