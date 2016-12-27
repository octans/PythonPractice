DROP DATABASE IF EXISTS `wanghong`;
CREATE DATABASE `wanghong` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
USE `wanghong`;
set names utf8mb4;


DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
    `id` INT UNSIGNED,
    `name` VARCHAR(100),
    `order` INT UNSIGNED,
    PRIMARY KEY (`id`)
);

#DROP TABLE IF EXISTS `Tbl_Huajiao_Live`;
CREATE TABLE `Tbl_Huajiao_Live` (
    `FLiveId` INT UNSIGNED NOT NULL,
    `FUserId` INT UNSIGNED NOT NULL,
    `FWatches` INT UNSIGNED NOT NULL DEFAULT 0  COMMENT '观看人数',
    `FPraises` INT UNSIGNED NOT NULL DEFAULT 0  COMMENT '赞数',
    `FReposts` INT UNSIGNED NOT NULL DEFAULT 0  COMMENT 'unknown',
    `FReplies` INT UNSIGNED NOT NULL DEFAULT 0  COMMENT 'unknown',
    `FPublishTimestamp` INT UNSIGNED NOT NULL COMMENT '发布日期',
    `FTitle` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '直播名称',
    `FImage` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '直播封面',
    `FLocation` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '地点',
    `FScrapedTime` timestamp NOT NULL COMMENT '爬虫更新时间',
    PRIMARY KEY (`FLiveId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

#DROP TABLE IF EXISTS `Tbl_Huajiao_User`;
CREATE TABLE `Tbl_Huajiao_User` (
    `FUserId` INT UNSIGNED NOT NULL,
    `FUserName` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '昵称',
    `FLevel` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '等级',
    `FFollow` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '关注数',
    `FFollowed` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '粉丝数',
    `FSupported` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '赞数',
    `FExperience` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '经验值',
    `FAvatar` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '头像地址',
    `FScrapedTime` timestamp NOT NULL COMMENT '爬虫时间',
    PRIMARY KEY (`FUserId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


## 主播汇总表
#DROP TABLE IF EXISTS `Tbl_Actor`;
CREATE TABLE `Tbl_Actor` (
    `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
    `uid` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '唯一标识用户',
    `nickname` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '昵称',
    `follow` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '关注数',
    `followed` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '粉丝数',
    `praised` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '被赞数',
    `avatar` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '头像',
    `pid` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '平台id, 1-花椒，2-一下',
    `scraped_time` timestamp NOT NULL COMMENT '爬虫更新时间',
    PRIMARY KEY (`id`),
    UNIQUE INDEX `INDEX_uid_pid` (`uid`, `pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

# 沃米优选主播表
#DROP TABLE IF EXISTS `Tbl_WMYX_Actor`;
CREATE TABLE `Tbl_WMYX_Actor` (
    `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
    `uuid` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '沃米优选唯一id',
    `user_id` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '平台id',
    `platform` TINYINT NOT NULL DEFAULT 0 COMMENT '直播平台',
    `nickname` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '昵称',
    `followed` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '粉丝数',
    `avg_watched` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '平均观看人数',
    `price_dict` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '推广方式和价格',
    `type_label` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '资源分类',
    `geo_range` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '推广覆盖地域',
    `sex` TINYINT NOT NULL DEFAULT 0 COMMENT '性别',
    `avatar` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '头像',
    `min_price` INT(10) UNSIGNED NOT NULL DEFAULT 0 COMMENT 'min_price',
    `max_price` INT(10) UNSIGNED NOT NULL DEFAULT 0 COMMENT 'max_price',
    `address` VARCHAR(30) NOT NULL DEFAULT '' COMMENT 'address',
    `scraped_time` timestamp NOT NULL COMMENT '爬虫更新时间',
    PRIMARY KEY (`id`),
    UNIQUE INDEX `INDEX_uuid` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

## 一下主播表
#DROP TABLE IF EXISTS `Tbl_YiXia_Actor`;
CREATE TABLE `Tbl_YiXia_Actor` (
    `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
    `uid` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '唯一标识用户',
    `suid` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '唯一标识用户',
    `nickname` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '昵称',
    `follow` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '关注数',
    `followed` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '粉丝数',
    `video_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '视频数',
    `relayed` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '转发数，主播转发被人的',
    `praised` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '被赞数',
    `location` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '位置',
    `avatar` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '头像',
    `descr` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '简介',
    `scraped_time` timestamp NOT NULL COMMENT '爬虫更新时间',
    PRIMARY KEY (`id`),
    UNIQUE INDEX `INDEX_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

## 一下视频表
#DROP TABLE IF EXISTS `Tbl_YiXia_Video`;
CREATE TABLE `Tbl_YiXia_Video` (
    `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
    `scid` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '唯一标识视频',
    `pub_date` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '发布日期',
    `watched` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '观看数',
    `praised` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '被赞数',
    `discussed` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '评论数',
    `img` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '封面',
    `title` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '标题',
    `detail_page` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '详情页',
    `flash` VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'falsh地址',
    `scraped_time` timestamp NOT NULL COMMENT '爬虫更新时间',
    PRIMARY KEY (`id`),
    UNIQUE INDEX `INDEX_scid` (`scid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;





