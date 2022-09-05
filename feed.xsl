<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html"/>
<xsl:template match="/">
    <html>
	 <head>
        <style>
	 main{
            padding-bottom: 10px; 
            margin-left: auto; 
            margin-right: auto; 
            max-width: 1200px; 
            display: flexbox; 
          }
          p {
            margin-block-start: 0.5em;
            margin-block-end: 0.5em;
            font-size: 1rem;
          }
          h2 {
            margin-block-start: 0.1em;
            margin-block-end: 0.1em;
            font-size: 1.4rem;
          }
          .feed {
            display: flexbox;
            gap: 20px;
          }
          @media (min-width: 1024px) {
            .feed {
              grid-template-columns: 1fr 1fr;
            }
          }
          .feed_card {
            position: relative;
            display: flexbox;
            padding: 10px;
          }
          .feed_card_inner::after {
            content: "";
            position: flexbox;
            bottom: 0;
            left: 0;
            right: 0;
            height: 100%;
            width: 100%;
          }
            .feed_card:hover {
            transform: scale(1.01);
          }
          .feed_card_inner {
            height: 100%;
            overflow-y: hidden;
            word-break: break-word;
            display: grid;
            gap: 10px;
            align-content: start;
          }
          .feed_description{
            font-family: 'Montserrat';
            font-size: 0.8rem;
            line-height: 100%;
          }
          small{
            font-size: 0.9rem;
            font-family: 'Montserrat';
          }
          @media (min-width: 550px) {
            main{
            padding: 0 10px 10px;
            }
            .feed {
            gap: 30px;
          }
            .feed_card_inner {
            height: 100%;
            }
            .card_inner {
            height: 100%;
            }
            .feed_description{
              font-size: 1.15rem;
            }
            small{
              font-size: 0.9rem;
            }
            .feed_card {
              padding: 26px;
            }
          }
          @media (min-width: 768px){
            padding: 0 30px 30px;
          }
        </style>
      </head>
      <body>
        <main>
          <div class="feed">
            <xsl:for-each select="rss/channel/item">
             <div class="feed_card">
                <div class="feed_card_inner">
                <a>
                  <xsl:attribute name="href">
                   <xsl:value-of select="link" />
                  </xsl:attribute>
                <br/>
				<h3>
                  <xsl:value-of select="title" />
                </h3>
                </a>
				<p>
				<xsl:attribute name="link">
                   <xsl:value-of select="link" />
                  </xsl:attribute>
				</p>
                <small>
                  <span>Publication date:
                  <b>
                    <xsl:value-of select="pubDate" />
                  </b>
                  </span>
                </small>
                <p>
				<small>
                  <span>Categories:
                  <b>
                    <xsl:value-of select="category" />
                  </b>
                  </span>
                </small> 
				<br/>
				<small>
                  <span>Link :
                  <b><a>
                  <xsl:attribute name="href">
                   <xsl:value-of select="link" />
                  </xsl:attribute>
                    <xsl:value-of select="link" />
                </a>
                  </b>
                  </span>
                </small> 
				</p>
               <p class="feed_description">
                  <xsl:value-of select="description" />
                </p>
                </div>
              </div>
            </xsl:for-each>
          </div>
        </main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
