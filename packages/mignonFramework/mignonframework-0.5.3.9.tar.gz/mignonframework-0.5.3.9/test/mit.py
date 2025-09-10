from mignonFramework import start


start()

"""
curl 'http://www.rizhao.gov.cn/jsearchfront/interfaces/cateSearch.do' \
  -H 'Accept: application/json, text/javascript, */*; q=0.01' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6,zh-TW;q=0.5' \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -b 'user_sid=1126a6c0e84943649a915e571e45342c; user_cid=0bbc0a2bf5f44d668cd5e00b416876aa; hq=%E6%B5%B7%E6%B4%8B; _city=%E9%9D%92%E5%B2%9B%E5%B8%82; JSESSIONID=0BADFBAF0F23C67DEC5B22E1B56D5C1D; searchsign=67ddf2738ba5424c8b4616caf1fbb766; sid=039e35ddb9887c591dc1443e90737d79; zh_choose_147=s; wzaFirst=1; _q=%u6D77%u6D0B%3A; zh_choose_undefined=s' \
  -H 'Origin: http://www.rizhao.gov.cn' \
  -H 'Pragma: no-cache' \
  -H 'Proxy-Connection: keep-alive' \
  -H 'Referer: http://www.rizhao.gov.cn/jsearchfront/search.do?websiteid=371100000000000&tpl=1541&q=%E6%B5%B7%E6%B4%8B&p=1&pg=&pos=title&searchid=6005&oq=&eq=&begin=&end=&sortFields=' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-raw 'websiteid=371100000000000&q=海洋&p=1&pg=10&cateid=16369&pos=title&pq=&oq=&eq=&begin=&end=&tpl=1541&sortFields=' \
  --insecure
"""