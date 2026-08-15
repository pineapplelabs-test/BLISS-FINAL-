import re

with open('index.html', 'r') as f:
    content = f.read()

# Extract head and nav
head_match = re.search(r'(<!DOCTYPE html>.*?</nav>)', content, re.DOTALL)
head_nav = head_match.group(1) if head_match else ""

# Extract footer
footer_match = re.search(r'(<!-- FOOTER -->.*?</html>)', content, re.DOTALL)
footer = footer_match.group(1) if footer_match else ""

blog_html = head_nav + """
  <section class="hero" style="min-height: 40vh; margin-top: 90px; padding: 60px 0;">
    <div class="container">
      <div class="hero-header fade-in">
        <span class="label">Our Stories</span>
        <h1 class="heading-xl hero-main-title">BLISS Blog</h1>
        <p class="hero-subtitle">News, updates, and inspiration from our Dance Studio and Party Hall.</p>
      </div>
    </div>
  </section>

  <section class="academy" style="padding: 40px 0 100px;">
    <div class="container">
      <div class="cards-grid" id="blog-grid">
        <!-- Posts will be injected here -->
        <p id="loading-msg">Loading posts...</p>
      </div>
    </div>
  </section>

  <script type="module">
    import { createClient } from 'https://esm.sh/@sanity/client'
    
    const client = createClient({
      projectId: 'ba1hmt7m',
      dataset: 'production',
      useCdn: true,
      apiVersion: '2023-05-03',
    })
    
    async function loadPosts() {
      try {
        const posts = await client.fetch('*[_type == "post"]{title, slug, mainImage{asset->{url}}, publishedAt, "excerpt": array::join(string::split((pt::text(body)), "")[0..100], "") + "..."} | order(publishedAt desc)')
        
        const grid = document.getElementById('blog-grid');
        grid.innerHTML = ''; // Clear loading
        
        if (posts.length === 0) {
            grid.innerHTML = '<p>No posts found.</p>';
            return;
        }

        posts.forEach(post => {
          const imageUrl = post.mainImage?.asset?.url || 'images/dance_hero_new.png';
          const date = new Date(post.publishedAt).toLocaleDateString();
          
          grid.innerHTML += `
            <a href="post.html?slug=${post.slug.current}" class="flash-card" style="text-decoration:none; color:inherit;">
              <div class="card-img-wrap">
                <img src="${imageUrl}" alt="${post.title}" />
              </div>
              <div class="card-content-wrap">
                <div class="card-category">${date}</div>
                <h3 class="card-title">${post.title}</h3>
                <p class="card-desc">${post.excerpt}</p>
                <span class="card-arrow">Read More &rarr;</span>
              </div>
            </a>
          `;
        });
      } catch (err) {
        console.error(err);
        document.getElementById('loading-msg').innerText = 'Error loading posts.';
      }
    }
    
    loadPosts();
  </script>
""" + footer

with open('blog.html', 'w') as f:
    f.write(blog_html)

post_html = head_nav + """
  <section class="hero" style="min-height: auto; margin-top: 90px; padding: 60px 0 20px;">
    <div class="container">
      <div class="hero-header fade-in" style="max-width: 800px; margin: 0 auto; text-align: left;">
        <span class="label" id="post-date">Loading...</span>
        <h1 class="heading-lg hero-main-title" id="post-title" style="margin-top:20px; margin-bottom: 20px;">Loading Post...</h1>
      </div>
    </div>
  </section>

  <section class="post-content" style="padding: 20px 0 100px;">
    <div class="container" style="max-width: 800px; margin: 0 auto;">
      <div id="post-image" style="margin-bottom: 40px; border-radius: 12px; overflow: hidden;"></div>
      <div id="post-body" style="font-size: 1.1rem; line-height: 1.8; color: var(--text-soft);">
      </div>
    </div>
  </section>

  <!-- Include Portable Text to HTML compiler -->
  <script src="https://unpkg.com/@portabletext/to-html@2.0.0/dist/index.umd.js"></script>
  
  <script type="module">
    import { createClient } from 'https://esm.sh/@sanity/client'
    
    const client = createClient({
      projectId: 'ba1hmt7m',
      dataset: 'production',
      useCdn: true,
      apiVersion: '2023-05-03',
    })
    
    async function loadPost() {
      const urlParams = new URLSearchParams(window.location.search);
      const slug = urlParams.get('slug');
      
      if (!slug) {
        document.getElementById('post-title').innerText = 'Post not found';
        return;
      }
      
      try {
        const post = await client.fetch(`*[_type == "post" && slug.current == "${slug}"][0]{
          title, mainImage{asset->{url}}, publishedAt, body
        }`);
        
        if (!post) {
          document.getElementById('post-title').innerText = 'Post not found';
          return;
        }
        
        document.getElementById('post-title').innerText = post.title;
        document.getElementById('post-date').innerText = new Date(post.publishedAt).toLocaleDateString();
        
        if (post.mainImage?.asset?.url) {
          document.getElementById('post-image').innerHTML = `<img src="${post.mainImage.asset.url}" style="width: 100%; height: auto;" alt="${post.title}" />`;
        }
        
        const htmlBody = window.PortableText.toHTML(post.body, {
           components: {
             types: {
               image: ({value}) => `<img src="https://cdn.sanity.io/images/ba1hmt7m/production/${value.asset._ref.replace('image-','').replace('-jpg','.jpg').replace('-png','.png')}" style="width:100%; border-radius:12px; margin:20px 0;" />`
             }
           }
        });
        document.getElementById('post-body').innerHTML = htmlBody;
        
      } catch (err) {
        console.error(err);
        document.getElementById('post-title').innerText = 'Error loading post';
      }
    }
    
    loadPost();
  </script>
""" + footer

with open('post.html', 'w') as f:
    f.write(post_html)

print("Created blog.html and post.html")
