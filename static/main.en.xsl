<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template name="header">
        <html>
            <head>
                <title>RuCTF Quals 2013</title>
                <base href="{/response/@base}" />
                <xsl:if test="/response/view[@type = 'monitor']">
                    <meta http-equiv="refresh" content="30;url=monitor" />
                </xsl:if>
                <link rel="stylesheet" type="text/css" href="static/qserver.css" />
                <script src="static/qserver.js" />
            </head>
            <body>
                <xsl:apply-templates select="/response" />
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
