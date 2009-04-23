<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:import href="main.xsl" />
    <xsl:import href="design-test.xsl" />
    <xsl:import href="viewers.xsl" />
    <xsl:template match="/">
        <xsl:call-template name="header" />
    </xsl:template>
    <xsl:template match="response[@type='design-test']">
        <xsl:call-template name="design-test" />
    </xsl:template>
</xsl:stylesheet>
