from .forms import CommentForm
from blog.models import Post
from django.shortcuts import render, get_object_or_404, redirect


# Create your views here.
def post_comment(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect(post)
            ##当 redirect 函数接收一个模型的实例时，它会调用这个模型实例的 get_absolute_url 方法，
            # 然后重定向到 get_absolute_url 方法返回的 URL。
        else:
            comment_list = post.comment_set.all()
            # post.comment_set.all()这个用法有点类似于 Post.objects.all()
            # 其作用是获取这篇 post 下的的全部评论， 因为 Post 和 Comment 是 ForeignKey 关联的，
            # 因此使用 post.comment_set.all() 反向查询全部评论
            context = {
                'post': post,
                'form': form,
                'comment_list': comment_list
            }
            return render(request, 'blog/detail.html', context=context)
    return redirect(post)
