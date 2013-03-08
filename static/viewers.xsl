<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:import href="login-view.xsl" />
    <xsl:import href="hello-view.xsl" />
    <xsl:import href="news-view.xsl" />
    <xsl:import href="error-view.xsl" />
    <xsl:import href="quest-list-view.xsl" />
    <xsl:import href="quest-view.xsl" />
    <xsl:import href="quest-check-view.xsl" />
    <xsl:import href="monitor-view.xsl" />
    <xsl:import href="jquest-list-view.xsl" />
    <xsl:import href="jquest-get-view.xsl" />
    <xsl:template match="response">
        <div class="page-wrapper">
            <xsl:apply-templates select="view" />
            <div class="page-pusher"></div>
        </div>
        <div class="page-footer"> &#169;RuCTF Team 2013 </div>
    </xsl:template>
</xsl:stylesheet>
