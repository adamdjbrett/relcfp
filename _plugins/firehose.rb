require "rexml/document"
require "time"

# Combine the rendered feeds so imported entries and curated HTML stay intact.
Jekyll::Hooks.register :site, :post_render do |site|
  firehose = site.pages.find { |page| page.url == "/firehose.xml" }
  combined = REXML::Document.new(firehose.output)
  entries = ["/posts/feed.atom", "/feed.xml"].flat_map do |url|
    page = site.pages.find { |candidate| candidate.url == url }
    feed = REXML::Document.new(page.output).root
    feed.get_elements("entry").each do |entry|
      if !entry.elements["author"] && feed.elements["author"]
        entry.add_element(feed.elements["author"].deep_clone)
      end
    end
  end
  entries.uniq! do |entry|
    link = entry.get_elements("link").find { |item| [nil, "alternate"].include?(item.attributes["rel"]) }
    (link ? link.attributes["href"] : entry.elements["id"].text).sub(%r{/$}, "")
  end
  entries.sort_by { |entry| Time.iso8601(entry.elements["updated"].text) }.reverse_each do |entry|
    combined.root.add_element(entry)
  end
  firehose.output = combined.to_s
end
