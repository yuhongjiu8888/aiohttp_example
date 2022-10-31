CREATE TABLE IF NOT EXISTS `tb_device`(
        `device_id` varchar(100) NOT NULL  COMMENT '设备ID号',
        `batch_id` varchar(100) NOT NULL  COMMENT '批次号',
        `oem_id` varchar(100) NOT NULL COMMENT '客户号OEM号',
        `active_code` varchar(256)  DEFAULT NULL COMMENT '激活码',
        `active_time` datetime DEFAULT NULL  COMMENT '激活时间',
        `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立时间',
        PRIMARY KEY ( `device_id` ),
        INDEX `device_id` (`device_id`) USING BTREE
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
ROW_FORMAT=DYNAMIC
;