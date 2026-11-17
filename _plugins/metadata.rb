require "cgi"
require "json"

module RelcfpMetadata
  def metadata_authors(value)
    site = @context.registers[:site]
    values = value.is_a?(Array) ? value : [value]
    authors = values.compact.map do |item|
      author = item.respond_to?(:keys) ? item : site.data.fetch("authors", {})[item]
      author = author ? author.to_h.dup : { "name" => item.to_s }
      author["type"] ||= "Person"
      author["url"] ||= author["website"] || author["uri"]
      author
    end.reject { |author| author["name"].to_s.strip.empty? }
    authors.empty? ? metadata_authors(site.config.fetch("author")) : authors
  end

  def page_metadata(page)
    site = @context.registers[:site]
    text = ->(value) { CGI.unescapeHTML(strip_html(value.to_s)).gsub(/\s+/, " ").strip }
    title = text.call(page["title"] || site.config["title"])
    description = text.call(page["description"] || page["excerpt"] || site.config["description"])
    description = text.call(site.config["description"]) if description.empty?
    authors = metadata_authors(page["author"])
    url = absolute_url(page["url"])
    canonical = absolute_url(page["canonical_url"] || page["url"]).sub(%r{/index\.html$}, "/")
    language = page["lang"] || site.config.fetch("lang", "en-US")
    post = page["layout"] == "post"
    published = date_to_xmlschema(page["date"]) if post && page["date"]
    modified = date_to_xmlschema(page["last_modified_at"]) if page["last_modified_at"]
    image_data = page["image"]
    image = image_data.respond_to?(:keys) ? image_data["path"] : image_data
    image = absolute_url(image) if image
    image_alt = image_data.respond_to?(:keys) ? image_data["alt"] || title : title
    home = absolute_url("/")
    publisher = { "@type" => "Organization", "@id" => home + "#organization",
                  "name" => site.config.dig("author", "name"), "url" => home,
                  "sameAs" => [site.config["facebook_url"], site.config["twitter_url"],
                               site.config["bksy_url"], "https://mastodon.social/@relcfp"].compact }
    website = { "@type" => "WebSite", "@id" => home + "#website", "url" => home,
                "name" => site.config["title"], "description" => site.config["description"].strip,
                "inLanguage" => site.config.fetch("lang", "en-US"),
                "publisher" => { "@id" => publisher["@id"] } }
    type = case page["url"]
           when "/about/" then "AboutPage"
           when "/posts/", "/tag/" then "CollectionPage"
           else "WebPage"
           end
    webpage = { "@type" => type, "@id" => url + "#webpage", "url" => url,
                "name" => title, "description" => description, "inLanguage" => language,
                "license" => "https://creativecommons.org/licenses/by/4.0/",
                "isPartOf" => { "@id" => website["@id"] } }
    graph = [publisher, website, webpage]
    breadcrumbs = []
    unless ["/", "/404.html"].include?(page["url"])
      breadcrumbs << { "name" => "Home", "url" => home }
      breadcrumbs << { "name" => "Posts", "url" => absolute_url("/posts/") } if post
      breadcrumbs << { "name" => title, "url" => url }
      breadcrumb_id = url + "#breadcrumbs"
      webpage["breadcrumb"] = { "@id" => breadcrumb_id }
      graph << { "@type" => "BreadcrumbList", "@id" => breadcrumb_id,
                 "itemListElement" => breadcrumbs.each_with_index.map do |crumb, index|
                   { "@type" => "ListItem", "position" => index + 1,
                     "name" => crumb["name"], "item" => crumb["url"] }
                 end }
    end
    if post || page["url"] == "/posts/"
      blog = { "@type" => "Blog", "@id" => absolute_url("/posts/#blog"),
               "url" => absolute_url("/posts/"), "name" => site.config["title"],
               "publisher" => { "@id" => publisher["@id"] } }
      graph << blog
      webpage["mainEntity"] = { "@id" => blog["@id"] } unless post
    end
    if post
      article = { "@type" => "BlogPosting", "@id" => url + "#article", "url" => url,
                  "headline" => title, "description" => description, "inLanguage" => language,
                  "mainEntityOfPage" => { "@id" => webpage["@id"] },
                  "isPartOf" => { "@id" => blog["@id"] },
                  "publisher" => { "@id" => publisher["@id"] },
                  "author" => authors.map do |author|
                    person = { "@type" => author["type"], "name" => author["name"] }
                    person["url"] = absolute_url(author["url"]) if author["url"]
                    person
                  end }
      article["datePublished"] = published if published
      article["dateModified"] = modified || published if modified || published
      article["image"] = image if image
      article["keywords"] = page["tags"] if page["tags"] && !page["tags"].empty?
      article["isBasedOn"] = canonical if canonical != url
      webpage["mainEntity"] = { "@id" => article["@id"] }
      graph << article
    end
    { "title" => title, "description" => description, "authors" => authors,
      "url" => url, "canonical" => canonical, "language" => language, "post" => post,
      "published" => published, "modified" => modified, "image" => image,
      "image_alt" => image_alt, "breadcrumbs" => breadcrumbs,
      "schema" => { "@context" => "https://schema.org", "@graph" => graph } }
  end

  def metadata_json(value)
    # Script contents use JSON escapes, since HTML entities would corrupt JSON-LD.
    JSON.pretty_generate(value).gsub("<", '\\u003c').gsub(">", '\\u003e').gsub("&", '\\u0026')
  end
end

Liquid::Template.register_filter(RelcfpMetadata)
