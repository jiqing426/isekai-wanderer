# CR-045 Tasks

## Implementation Tasks

| Task ID | Owner Agent | Requirement / AC | Excluded AC | Allowed Write Scope | Test Case Artifact | Verification | Rollback / Revert Plan | Status |
|---------|-------------|-----------------|-------------|---------------------|--------------------|-------------|----------------------|--------|
| DEV-001 | ops | REQ-001, AC-001, AC-002, AC-003 | 无 | admin.bak/, .gitignore | 无（纯运维操作） | du -sh admin.bak 不存在; git check-ignore admin/node_modules | git checkout admin.bak | Ready |
| DEV-002 | backend | REQ-002, AC-004, AC-005, AC-006 | 无 | backend/app/api/v1/subscription.py, backend/app/api/v1/user_subscription.py, backend/app/api/v1/cr016_subscription.py | backend/tests/unit/test_deprecated_endpoints.py | grep create_order subscription.py 返回空; grep fragment-purchase 返回空 | git revert | Ready |
| DEV-003 | frontend | REQ-003, AC-007, AC-008 | 无 | frontend/src/components/paywall/PaywallManager.vue, frontend/src/components/paywall/QuotaExhaustedModal.vue, frontend/src/components/QuotaDisplay.vue | frontend/tests/unit/component-cleanup.spec.ts | grep QuotaExhaustedModal 返回空 | git revert | Ready |
| DEV-004 | backend | REQ-004, AC-009, AC-010 | 无 | backend/app/**/*.py, frontend/src/**/*.vue, frontend/src/**/*.ts | backend/tests/unit/test_no_print.py | grep "^\s*print(" backend/app 返回 0; console.log < 5 | git revert | Ready |
| DEV-005 | frontend | REQ-005, AC-011, AC-012, AC-013 | 无 | frontend/src/components/AppHeader.vue, frontend/src/components/SubscriptionPlans.vue, frontend/src/router/index.ts | frontend/tests/unit/bug-fixes.spec.ts | E2E: toast 不重复; 语言下拉正常; /profile 重定向 | git revert | Ready |
