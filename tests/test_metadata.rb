require "jekyll"
require "time"
require_relative "../_plugins/metadata"

site = Jekyll::Site.new(Jekyll.configuration("baseurl" => "/preview", "quiet" => true))
site.data["authors"] = { "known" => { "name" => "Known Author", "website" => "https://example.org/author" } }
registers = { site: site }
render = ->(template, page) { Liquid::Template.parse(template).render!({ "page" => page }, registers: registers) }
metadata = ->(page) { JSON.parse(render.call("{{ page | page_metadata | metadata_json }}", page)) }
check = ->(condition, message) { raise message unless condition }
base = { "layout" => "post", "url" => "/example/", "title" => 'Quotes " & Unicode — </script><script>alert(1)</script>',
         "description" => "<p>A &amp; B\n with markup</p>", "date" => Time.iso8601("2026-11-12T12:00:00-06:00") }

[
  [nil, ["RELCFP"]], ["", ["RELCFP"]], [[], ["RELCFP"]],
  ["known", ["Known Author"]], ["Unlisted Author", ["Unlisted Author"]],
  [{ "name" => "Inline Author", "uri" => "https://example.org" }, ["Inline Author"]],
  [["known", { "name" => "Second Author" }], ["Known Author", "Second Author"]]
].each do |author, names|
  data = metadata.call(base.merge("author" => author))
  check.call(data["authors"].map { |item| item["name"] } == names, "Incorrect author resolution")
  article = data["schema"]["@graph"].find { |node| node["@type"] == "BlogPosting" }
  check.call(article["author"].map { |item| item["name"] } == names, "Schema author mismatch")
  check.call(article["datePublished"] == "2026-11-12T12:00:00-06:00", "Lost date timezone")
  check.call(!article.key?("image"), "Invented image")
end

data = metadata.call(base)
check.call(data["description"] == "A & B with markup", "Description must be plain text")
check.call(data["url"] == "https://relcfp.com/preview/example/", "Lost baseurl")
check.call(data["authors"][0]["type"] == "Organization", "Site author is an organization")
raw = render.call("{{ page | page_metadata | metadata_json }}", base)
check.call(!raw.include?("\n"), "JSON-LD must be compact")
check.call(!raw.include?("</script>"), "JSON-LD can close its script element")
check.call(JSON.parse(raw)["title"].include?('Quotes " & Unicode —'), "JSON escaping changed text")
unsafe_author = 'An "author" & </script><script>alert(1)</script>'
unsafe_page = base.merge("author" => ["known", unsafe_author])
raw = render.call("{{ page | page_metadata | metadata_json }}", unsafe_page)
check.call(!raw.include?("</script>") && JSON.parse(raw)["authors"][1]["name"] == unsafe_author, "Unsafe author JSON or changed name")
html = Liquid::Template.parse(File.read(File.expand_path("../_includes/metadata.html", __dir__))).render!(
  { "page" => unsafe_page, "metadata" => metadata.call(unsafe_page), "site" => site.site_payload["site"] }, registers: registers
)
check.call(html.scan("</script>").length == 1, "Metadata can inject a script element")
check.call(html.include?(CGI.escapeHTML(unsafe_author)) && html.scan('name="citation_author"').length == 2, "Citation authors must be escaped and repeated")

data = metadata.call(base.merge("author" => "known", "lang" => "fr-FR", "last_modified_at" => "2026-11-15T09:00:00Z",
                                "image" => { "path" => "/cover.png", "alt" => 'A "cover"' },
                                "canonical_url" => "https://source.example/call/", "tags" => ["religion", "theology"]))
article = data["schema"]["@graph"].find { |node| node["@type"] == "BlogPosting" }
check.call(data["canonical"] == article["isBasedOn"] && data["canonical"] == "https://source.example/call/", "Lost source canonical")
check.call(article["url"] == data["url"], "Source replaced the curated post identity")
check.call(article["author"][0]["url"] == "https://example.org/author", "Lost author URL")
check.call(article["image"] == "https://relcfp.com/preview/cover.png" && data["image_alt"] == 'A "cover"', "Incorrect image metadata")
check.call(Time.iso8601(article["dateModified"]) == Time.iso8601("2026-11-15T09:00:00Z") && article["inLanguage"] == "fr-FR", "Lost modified date or language")
check.call(article["keywords"] == ["religion", "theology"], "Lost tags")

data = metadata.call({ "url" => "/about/", "title" => "About", "layout" => "page" })
check.call(data["schema"]["@graph"].any? { |node| node["@type"] == "AboutPage" }, "Wrong page type")
check.call(!data["post"] && data["published"].nil?, "Invented post or publication date")
check.call(!metadata.call(base.merge("description" => "<p> </p>"))["description"].empty?, "Empty excerpt needs site description")
["/", "/404.html"].each do |url|
  check.call(metadata.call({ "url" => url })["breadcrumbs"].empty?, "Invalid homepage/404 breadcrumbs")
end
puts "Metadata author variants, safe JSON, canonical sources, baseurl, dates, language, and optional fields verified."
