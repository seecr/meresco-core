
CRLF = "\r\n"
ContentTypeXml = "Content-Type: text/xml; charset=utf-8"
ContentTypeRss = "Content-Type: application/rss+xml"
ContentTypeHtml = "Content-Type: text/html; charset=utf-8"

#200
okXml = "HTTP/1.0 200 Ok" + CRLF + \
        ContentTypeXml + CRLF + \
        CRLF

okRss = "HTTP/1.0 200 Ok" + CRLF + \
        ContentTypeRss + CRLF + \
        CRLF

#404
notFoundHtml = "HTTP/1.0 404 Not Found" + CRLF + \
               ContentTypeHtml + CRLF + \
               CRLF

#500
serverErrorXml = "HTTP/1.0 500 Internal Server Error" + CRLF +\
                 ContentTypeXml + CRLF + \
                 CRLF
