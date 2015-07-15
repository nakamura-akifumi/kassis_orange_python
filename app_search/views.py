from django.shortcuts import render_to_response, redirect
import riak
import urllib, json
import urllib.parse
import urllib.request
from importer.models import ndl_search_opensearch
import pprint
from django.core.context_processors import csrf
from django.http import HttpResponseNotFound
from django.conf import settings
from app_search.helpers.message_helper import message
from django.http import HttpResponse
from app_search.helpers.solr_helper import SolrHelper
from app_search.helpers.paginate_helper import Paginate

def m_show(request, m_id=None, format='html'):
    client = riak.RiakClient()
    bucket = client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(settings.RIAK["STORE_BUCKET"])

    #print("m_id={} format={}".format(m_id, format))

    m = bucket.get(m_id)
    if m == None or m.exists == False:
        return HttpResponseNotFound(render_to_response('404.html'))

    if request.method == 'POST' and request.POST["_method"] == "DELETE":
        print("delete object id={0}".format(m_id))
        m.delete()
        message.flash(request, "削除に成功しました", "success")
        return redirect('home')

    #
    page = {}
    page.update(message.get_flash_message(request))

    c = {}
    c.update(csrf(request))
    c.update({"m": m.data})
    c.update({"page": page})

    if format == "json":
        return HttpResponse(json.dumps(m.data, ensure_ascii=False, indent=2), content_type='application/json; encoding=utf-8')
    else:
        return render_to_response('search/show.jinja', c)

def m_import_from_ndl_rss(request):
    if request.method == 'POST':
        url = request.POST["url"]
        url = url.strip()
        import_logger = ndl_search_opensearch.NdlHelper.imoprt_from_rss(url)
        if import_logger:
            message.flash(request, "インポートに成功しました", "success")
            return redirect('home')
        else:
            message.flash(request, "インポートに失敗しました", "danger")

    c = {}
    c.update(csrf(request))
    page = {}
    page.update({"url":"http://iss.ndl.go.jp/rss/ndlopac/index.xml"})
    page.update(message.get_flash_message(request))
    c["page"] = page
    return render_to_response('search/m_import_rss.jinja', c)

def m_import_isbn(request):
    page = {}
    if request.method == 'POST':
        isbn = request.POST["isbn"]
        isbn = isbn.strip()
        m = ndl_search_opensearch.NdlHelper.import_from_net_by_isbn(isbn)
        if m:
            message.flash(request, "インポートに成功しました", "success")
            return redirect('m_show', m_id=m.key)
        else:
            message.flash(request, "インポートに失敗しました", "danger")

    c = {}
    c.update(csrf(request))
    page = {}
    page.update(message.get_flash_message(request))
    c["page"] = page
    return render_to_response('search/m_import_isbn.jinja', c)

def search_index(request):
    page = {"q": ""}
    page.update(message.get_flash_message(request))

    u = request.user

    return render_to_response('search/search_index.jinja',
                              {"page": page, "user": u}
                              )

def search_results(request):
    pp = pprint.PrettyPrinter()
    client = riak.RiakClient()
    bucket = client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(settings.RIAK["STORE_BUCKET"])

    params = request.GET

    solr_server_url = "http://localhost:8098"
    query_interface = "search/query/{0}".format(settings.RIAK["STORE_BUCKET_TYPE"])

    # 検索クエリの作成
    query_ss = []

    if 'q' not in params or ('q' in params and params['q'].strip() == ""):
        query_ss.append(("q","*:*"))
    else:
        query_ss.append(("q","{1}:{0} OR {2}:{0} OR {3}:{0}".format(params["q"].strip(), 'titles_ja', 'creators_ts', 'identifiers_ts')))

    PAGER_DEFAULT = 10
    START_PAGE_DEFAULT = 1
    SORT_DEFAULT = next(filter(lambda x:x['key'] == "ma", SolrHelper.SEARCH_RESULTS_SORT), None)['v']

    per_page = PAGER_DEFAULT
    current_page = START_PAGE_DEFAULT
    params_o1 = ""
    params_o2 = ""
    params_p = ""
    if 'o1' in params:
        params_o1 = params['o1']
        try:
            per_page = int(next(filter(lambda x:x['key'] == params_o1, SolrHelper.SEARCH_RESULTS_PAGES), PAGER_DEFAULT)['v'])
        except ValueError as e:
            pass

    sort_method = SORT_DEFAULT
    if 'o2' in params:
        params_o2 = params['o2']
        if type(params_o2) == "array":
            params_o2 = params_o2[0]
        if params_o2 == "ma":
            sort_method = next(filter(lambda x:x['key'] == params_o2, SolrHelper.SEARCH_RESULTS_SORT), SORT_DEFAULT)['v']
        else:
            sort_method = "{0},{1}"\
                    .format(next(filter(lambda x:x['key'] == params_o2, SolrHelper.SEARCH_RESULTS_SORT), SORT_DEFAULT)['v']
                                           , SORT_DEFAULT)

    if 'p' in params:
        try:
            current_page = int(params['p'])
            if current_page < 1:
                raise ValueError
            params_p = params['p']
        except ValueError as e:
            pass

    start_pos = per_page * (current_page - 1)

    # その他のオプション
    query_exts = [("wt","json"),
                  ('json.nl', 'arrmap'),
                  ('fl', '_yz_rk'),
                  ('rows', per_page),
                  ('sort', sort_method),
                  ('start', start_pos),
                 ]

    #
    querys = []
    querys.extend(query_ss)
    querys.extend(query_exts)

    search_url = "{0}/{1}?{2}".format(solr_server_url, query_interface, urllib.parse.urlencode(querys))
    print(search_url)

    enc = "UTF-8"

    sock = urllib.request.urlopen(search_url)
    results = json.loads(sock.read().decode(enc))
    sock.close()

    #print(results)
    manifestations = []
    result_count = 0
    if 'response' in results and results['response']['numFound'] and results['response']['numFound'] > 0:
        result_count = results['response']['numFound']

        for result in results['response']['docs']:
            m = bucket.get(result['_yz_rk'])
            if m and m.data:
                manifestations.append(m.data)
            else:
                print("warning: no document! key={0}".format(result['_yz_rk']))

    # ===

    paginate = Paginate()

    pageinfo = {"search_result_count": result_count,
                "q": params["q"],
                "o1": params_o1,
                "o2": params_o2,
                "p": params_p,
                "o1list": SolrHelper.SEARCH_RESULTS_PAGES,
                "o2list": SolrHelper.SEARCH_RESULTS_SORT,
                }
    pageinfo.update(paginate.paginate(result_count, current_page))
    return render_to_response('search/search_result.jinja',
                              {"manifestations": manifestations, "page": pageinfo}
                              )
