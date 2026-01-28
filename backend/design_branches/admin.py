from django.contrib import admin
from .models import (
    DesignBranch, DesignCommit, BranchMerge, MergeConflict,
    BranchReview, ReviewComment, DesignTag, BranchComparison
)

# Register models with basic admin
admin.site.register(DesignBranch)
admin.site.register(DesignCommit)
admin.site.register(BranchMerge)
admin.site.register(MergeConflict)
admin.site.register(BranchReview)
admin.site.register(ReviewComment)
admin.site.register(DesignTag)
admin.site.register(BranchComparison)
