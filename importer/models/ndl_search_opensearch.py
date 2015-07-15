from lxml import etree
import regex
from ast import literal_eval
import riak
from django.conf import settings
import urllib
import urllib.parse
import urllib.request
from importer.models.manifestation import Manifestation
from app_search.helpers.solr_helper import SolrHelper

class NdlHelper:
    # namespaces
    NS = {
        'lom': 'http://ltsc.ieee.org/xsd/LOM',
        'zs': 'http://www.loc.gov/zing/srw/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'voc': 'http://www.schooletc.co.uk/vocabularies/',
        'srw_dc': 'info:srw/schema/1/dc-schema',
        'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        'dcndl': "http://ndl.go.jp/dcndl/terms/",
        'dcterms': "http://purl.org/dc/terms/",
        'foaf': "http://xmlns.com/foaf/0.1/",
        'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
    }
    ROLE_LABELS = ["著"]

    def import_from_net_by_isbn(isbn):
        riak_obj = None
        meta = NdlHelper._import_from_net_by_isbn(isbn)

        if meta:
            client = riak.RiakClient()
            bucket = client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(settings.RIAK["STORE_BUCKET"])

            q = "source_identifier:{0}".format(SolrHelper.escape(meta["source_identifier"]))
            results = client.fulltext_search(settings.RIAK["STORE_BUCKET_TYPE"], q)
            if results["num_found"] > 0:
                print("already exist: find by resouce_identifier ({1}) isbn=({0})".format(isbn, meta["source_identifier"]))
                doc = results["docs"][0]
                m = bucket.get(doc["_yz_rk"])

                m = Manifestation(meta, doc["_yz_rk"], bucket, m)
                riak_obj = m.store()

            else:
                m = Manifestation(meta, None, None, None)
                riak_obj = m.store()

        return riak_obj

    def _import_from_net_by_isbn(isbn):
        # sru を使ってインポートをする
        # http://iss.ndl.go.jp/information/wp-content/uploads/2014/12/ndlsearch_api_20141215_jp.pdf
        # http://iss.ndl.go.jp/api/sru?operation=searchRetrieve&recordSchema=dcndl&maximumRecords=1&recordPacking=xml&query=isbn%3d4822247570
        # http://iss.ndl.go.jp/api/sru?operation=searchRetrieve&recordSchema=dcndl&maximumRecords=1&recordPacking=xml&query=isbn%3d4621087088

        # attr.tag attr.attrib attr.text
        # pp = pprint.PrettyPrinter(indent=2)

        server = "http://iss.ndl.go.jp"
        api_prefix = "/api/sru"
        api_query = "?operation=searchRetrieve&recordSchema=dcndl&maximumRecords=1&recordPacking=xml" \
                    "&version=1.2&onlyBib=true&query=isbn%3d{0}".format(isbn)
        search_url = "{0}{1}{2}".format(server, api_prefix, api_query)

        #print("search_url={}".format(search_url))

        sock = urllib.request.urlopen(search_url)
        results = sock.read()
        sock.close()

        doc = etree.fromstring(results)

        # check entry
        value = "".join([str(d) for d in doc.xpath("//zs:numberOfRecords/text()", namespaces = NdlHelper.NS)])
        if value in ("", "0"):
            print("no record. isbn={}".format(isbn))
            return None # no record
        #
        meta = {"record_source": "NDL", "record_source_sub": "SRU_ISBN"}

        # title
        value = " ".join([d.text for d in doc.xpath("//dc:title/rdf:Description/rdf:value", namespaces = NdlHelper.NS)])
        meta["title"] = value
        value = " ".join([d.text for d in doc.xpath("//dc:title/rdf:Description/dcndl:transcription", namespaces = NdlHelper.NS)])
        meta["title_transcription"] = value

        value = " ".join([d.text for d in doc.xpath("//dcndl:alternative/rdf:Description/rdf:value", namespaces = NdlHelper.NS)])
        meta["alternative"] = value

        value = " ".join([d.text for d in doc.xpath("//dcndl:alternative/rdf:Description/dcndl:transcription", namespaces = NdlHelper.NS)])
        meta["alternative_transcription"] = value

        # volume/edition
        value = " ".join([d.text for d in doc.xpath("//dcndl:volume/rdf:Description/rdf:value", namespaces = NdlHelper.NS)])
        meta["volume"] = value
        value = " ".join([d.text for d in doc.xpath("//dcndl:BibResource/dcndl:edition", namespaces = NdlHelper.NS)])
        meta["edition"] = value

        value = " ".join([d.text for d in doc.xpath("//dcndl:BibResource/dcndl:price", namespaces = NdlHelper.NS)])
        meta["price"] = value

        value = " ".join([d.text for d in doc.xpath("//dcndl:BibResource/dcterms:extent", namespaces = NdlHelper.NS)])
        meta["extent"] = value

        #
        value = " ".join([d.text for d in doc.xpath("//dcterms:date", namespaces = NdlHelper.NS)])
        meta["pub_date"] = value

        value = " ".join([d for d in doc.xpath("//dcndl:materialType/@rdfs:label", namespaces = NdlHelper.NS)])
        meta["material"] = value

        # link
        for d in doc.xpath("//dcndl:BibAdminResource", namespaces = NdlHelper.NS):
            xmlattr_t = literal_eval(str(d.attrib))
            for k, v in xmlattr_t.items():
                if regex.sub(r'(?<rec>\{(?:[^{}]+|(?&rec))*\})', "", k) == "about":
                    meta["source_link"] = v
                    meta["source_identifier"] = v


        # languages
        languages = {}
        value = " ".join([d.text for d in doc.xpath("//dcndl:BibResource/dcterms:language", namespaces = NdlHelper.NS)])
        if value != "":
            languages["body"] = value.upper()

        value = " ".join([d.text for d in doc.xpath("//dcndl:BibResource/dcndl:originalLanguage", namespaces = NdlHelper.NS)])
        if value != "":
            languages["original"] = value.upper()

        meta["languages"] = languages

        # identifiers (1)
        identifiers = {}
        values = doc.xpath("//dcndl:BibResource/dcterms:identifier", namespaces = NdlHelper.NS)
        for attr in values:
            xmlattr_t = literal_eval(str(attr.attrib))
            for k, v in xmlattr_t.items():
                if v in ["http://ndl.go.jp/dcndl/terms/JPNO","http://ndl.go.jp/dcndl/terms/ISBN",
                         "http://ndl.go.jp/dcndl/terms/TRCMARCNO",
                        ]:
                    #print(attr.text)
                    m = regex.match(r".*/(.+?$)", v)
                    if m != None:
                        identifiers.update({m.group(1): attr.text})

        # identifiers (2)
        for doc_subject in doc.xpath('//dcndl:BibResource/dcterms:subject', namespaces = NdlHelper.NS):
            xmlattr_t = literal_eval(str(doc_subject.attrib))
            for k, v in xmlattr_t.items():
                if regex.sub(r'(?<rec>\{(?:[^{}]+|(?&rec))*\})', "", k) == "resource":
                    m = regex.match(r"^http:\/\/id.ndl.go.jp\/class\/(.*)\/(.*)$", v)
                    if m:
                        identifiers.update({m.group(1).upper(): m.group(2)})

        # creators
        creators = []
        for d in doc.xpath('//dcterms:creator/foaf:Agent', namespaces = NdlHelper.NS):
            full_name = " ".join([d.text for d in d.xpath("./foaf:name", namespaces = NdlHelper.NS)])
            full_name_transcription = " ".join([d.text for d in d.xpath("./dcndl:transcription", namespaces = NdlHelper.NS)])

            creators.append({"full_name": full_name, "full_name_transcription": full_name_transcription})

        # description creators
        desc_creators = []
        for d in doc.xpath('//dc:creator', namespaces = NdlHelper.NS):
            print("desc_c={0}".format(d.text))
            values = str(d.text).rsplit(None, 1)
            print(values)
            print(len(values))
            full_name = ""
            role = ""
            if len(values) >= 1:
                full_name = values[0]
            if len(values) == 2:
                role = values[1]

            print("name={} role={}".format(full_name, role))
            desc_creators.append({"full_name": full_name, "role": role})

        # publishers
        publishers = []
        for doc_publisher in doc.xpath('//dcterms:publisher/foaf:Agent', namespaces = NdlHelper.NS):
            full_name = " ".join([d.text for d in doc_publisher.xpath("./foaf:name", namespaces = NdlHelper.NS)])
            full_name_transcription = " ".join([d.text for d in doc_publisher.xpath("./dcndl:transcription", namespaces = NdlHelper.NS)])
            role =  " ".join([d.text for d in doc_publisher.xpath("./dcterms:description", namespaces = NdlHelper.NS)])
            location =  " ".join([d.text for d in doc_publisher.xpath("./dcndl:location", namespaces = NdlHelper.NS)])

            publishers.append({"full_name": full_name, "full_name_transcription": full_name_transcription, "role": role, "location": location})


        # subjects
        subjects = []
        subject_pointer = ""
        for doc_subjects in doc.xpath('//dcndl:BibResource/dcterms:subject', namespaces = NdlHelper.NS):
            for d in doc_subjects.xpath("./rdf:Description", namespaces = NdlHelper.NS):
                subject_pointer = ""

                xmlattr_t = literal_eval(str(d.attrib))
                xmlattr_key = ""
                xmlattr_body = ""
                for keyname in xmlattr_t.keys():
                    xmlattr_key = regex.sub(r'(?<rec>\{(?:[^{}]+|(?&rec))*\})', "", keyname)
                    xmlattr_body = xmlattr_t[keyname]

                if xmlattr_key == "about":
                    subject_pointer = xmlattr_body

            value = " ".join([d.text for d in doc_subjects.xpath("./rdf:Description/rdf:value", namespaces = NdlHelper.NS)])

            if value != "":
                subjects.append({"pointer": subject_pointer, "value": value})

        # series
        value = " ".join([d.text for d in doc.xpath("//dcndl:seriesTitle/rdf:Description/rdf:value", namespaces = NdlHelper.NS)])
        meta["series_title"] = value

        value = " ".join([d.text for d in doc.xpath("//dcndl:seriesTitle/rdf:Description/dcndl:transcription", namespaces = NdlHelper.NS)])
        meta["series_title_transcription"] = value

        # その他
        descriptions = []
        for d in doc.xpath('//dcndl:BibResource/dcterms:description', namespaces = NdlHelper.NS):
            descriptions.append({"content": d.text})

        meta["descriptions"] = descriptions
        meta["identifiers"] = identifiers
        meta["subjects"] = subjects
        meta["publishers"] = publishers
        meta["creators"] = creators
        meta["desc_creators"] = desc_creators

        return meta

    def imoprt_from_rss(rss_url = "http://iss.ndl.go.jp/rss/ndlopac/index.xml"):
        """
        NDL RSS配信 全国書誌 からの取得
        http://www.ndl.go.jp/jp/library/data/jnb.html#iss03
        """
        sock = urllib.request.urlopen(rss_url)
        results = sock.read()
        sock.close()

        doc = etree.fromstring(results)
        return NdlHelper._import_from_xml(doc)

    def import_from_file(file_name):
        """
        NDL OpenSearchの結果をXMLファイルにしたものから取得
        """
        doc = etree.parse(file_name)
        return NdlHelper._import_from_xml(doc)

    def _import_from_xml(doc):
        client = riak.RiakClient()
        bucket = client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(settings.RIAK["STORE_BUCKET"])

        record_count = 0
        success_count = 0
        updated_count = 0
        created_count = 0
        items = doc.xpath("//item")
        for item in items:
            meta = {"record_source": "NDL", "record_source_sub": "OPENSEARCH_XMLFILE"}
            creators = []
            publishers = []
            identifiers = {}
            subjects = []
            desc_creators = []
            languages = {"body": "jpn"}
            descriptions = []

            for attr in item:
                #print('(1) element={0} attr={1} body={2}'.format(attr.tag, attr.attrib, attr.text))

                tag = regex.sub(r'(?<rec>\{(?:[^{}]+|(?&rec))*\})', "", attr.tag)
                xmlattr_t = literal_eval(str(attr.attrib))
                xmlattr_key = ""
                xmlattr_body = ""
                for keyname in xmlattr_t.keys():
                    xmlattr_key = regex.sub(r'(?<rec>\{(?:[^{}]+|(?&rec))*\})', "", keyname)
                    xmlattr_body = xmlattr_t[keyname]

                if tag == "title":
                    meta["title"] = attr.text
                elif tag == "titleTranscription":
                    meta["title_transcription"] = attr.text
                elif tag == "category":
                    meta["category"] = attr.text
                elif tag == "publisher":
                    if len(publishers) == 0:
                        publishers.append({"full_name": attr.text, "full_name_transcription": "", "role": "", "location": ""})
                elif tag == "publicationPlace":
                    if len(publishers) == 0:
                        publishers.append({"full_name": "", "full_name_transcription": "", "role": "", "location": attr.text})
                    else:
                        p = publishers[0]
                        p.update({"location": attr.text})
                elif tag == "pubDate":
                    meta["pub_date"] = attr.text
                elif tag == "dcndl:volume":
                    meta["volume"] = attr.text
                elif tag == "dcndl:edition":
                    meta["edition"] = attr.text
                elif tag == "seriesTitle":
                    meta["series_title"] = attr.text
                elif tag == "seriesTitleTranscription":
                    meta["series_title_transcription"] = attr.text
                elif tag == "subject":
                    if xmlattr_key == "":
                        subjects.append({"value": attr.text})
                    elif xmlattr_key == "type" and xmlattr_body in ["dcndl:NDC9","dcndl:NDC8"]:
                        akey = regex.sub(r'^.*?:', "", xmlattr_body)
                        identifiers.update({akey: attr.text})
                elif tag == "identifier":
                    if xmlattr_key == "type" and xmlattr_body in ["dcndl:JPNO","dcndl:ISBN","dcndl:TRCMARCNO"]:
                        akey = regex.sub(r'^.*?:', "", xmlattr_body)
                        identifiers.update({akey: attr.text})
                elif tag == "link":
                    meta["source_link"] = attr.text
                    meta["source_identifier"] = attr.text
                elif tag == "description":
                    descriptions.append({"content": attr.text})
                elif tag == "author":
                    authors = str(attr.text).split(",")
                    print("desc_c={0}".format(authors))
                    for a in authors:
                        values = str(a).rsplit(None, 1)
                        #print(values)
                        #print(len(values))
                        full_name = ""
                        role = ""
                        if len(values) >= 1:
                            full_name = values[0]
                        if len(values) == 2:
                            role = values[1]

                        #print("name={} role={}".format(full_name, role))
                        desc_creators.append({"full_name": full_name, "role": role})
                elif tag == "creator":
                    m = regex.match(r"(.*)[/／](.*)", attr.text)
                    if m != None:
                        name = m.group(1)
                        role = m.group(2)
                        creators.append({"full_name": name, "role": role})
                elif tag == "extent":
                    meta["extent"] = attr.text
                elif tag == "price":
                    meta["price"] = attr.text


            # end for item
            #meta["languages"] = languages
            meta["descriptions"] = descriptions
            meta["identifiers"] = identifiers
            meta["subjects"] = subjects
            meta["publishers"] = publishers
            meta["creators"] = creators
            meta["desc_creators"] = desc_creators

            # check
            q = "source_identifier:{0}".format(SolrHelper.escape(meta["source_identifier"]))
            results = client.fulltext_search(settings.RIAK["STORE_BUCKET_TYPE"], q)
            if results["num_found"] > 0:
                print("already exist: find by resouce_identifier ({0})".format(meta["source_identifier"]))
                doc = results["docs"][0]
                m = bucket.get(doc["_yz_rk"])
                m = Manifestation(meta, doc["_yz_rk"], bucket, m)
                riak_obj = m.store()
                updated_count += 1
            else:
                m = Manifestation(meta, None, None, None)
                riak_obj = m.store()
                created_count += 1

            print("manifestation stored success. key=%s" % (riak_obj.key))
            record_count += 1
            success_count += 1
        # end for
        results = {"record_count": record_count,
                   "success_count": success_count,
                   "updated_count": updated_count,
                   "created_count": created_count}
        print(results)
        return results
    #end def
# end class
