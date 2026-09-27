CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE;

MERGE (r:Regulation:Entity {id:'reg:soc2'})
SET r.name = 'SOC 2 Type II', r.framework = 'SOC 2';

MERGE (req:Requirement:Entity {id:'req:cc6.1'})
SET req.name = 'CC6.1 Logical Access';

MERGE (c:Control:Entity {id:'ctl:mfa'})
SET c.name = 'MFA Enforcement';

MERGE (i:Infrastructure:Entity {id:'infra:aws-iam'})
SET i.name = 'AWS IAM';

MERGE (e:Evidence:Entity {id:'ev:cloudtrail-iam'})
SET e.name = 'CloudTrail PutGroupPolicy';

MERGE (r)-[:GOVERNS {valid_start: date('2024-01-01'), system_start: date('2024-11-01')}]->(req)
MERGE (req)-[:SATISFIED_BY {valid_start: date('2025-01-01'), system_start: date('2025-07-15')}]->(c)
MERGE (c)-[:DEPENDS_ON {valid_start: date('2025-01-01'), system_start: date('2025-04-12')}]->(i)
MERGE (c)-[:EVIDENCED_BY {valid_start: date('2025-04-12'), system_start: date('2025-04-12')}]->(e);
