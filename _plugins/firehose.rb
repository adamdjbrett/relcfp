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
      authors = entry.get_elements("author")
      authors.each do |author|
        entry.delete_element(author) if author.elements["name"]&.text.to_s.strip.empty?
      end
      if entry.get_elements("author").empty?
        fallback = feed.get_elements("author").find { |author| !author.elements["name"]&.text.to_s.strip.empty? }
        if fallback
          entry.add_element(fallback.deep_clone)
        else
          entry.add_element("author").add_element("name").text = site.config.dig("author", "name")
        end
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
