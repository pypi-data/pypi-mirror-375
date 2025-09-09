/**
 * Jupyter MCP扩展的主入口文件
 */

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILayoutRestorer
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget, WidgetTracker } from '@jupyterlab/apputils';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { INotebookTracker } from '@jupyterlab/notebook';
import { Menu } from '@lumino/widgets';
import { McpConfigPanelWidget } from './mcp-config-panel';
import { McpChatPanelWidget } from './mcp-chat-panel';
import { McpManager, IMcpConfig } from './mcp-manager';

/**
 * 插件ID
 */
const PLUGIN_ID = 'Jupyterchatzz:plugin';

/**
 * 命令ID
 */
namespace CommandIDs {
  export const openConfig = 'mcp:open-config';
  export const connect = 'mcp:connect';
  export const disconnect = 'mcp:disconnect';
  export const openChatPanel = 'mcp:open-chat-panel';
}

/**
 * Jupyter MCP扩展插件
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  description: 'Jupyter MCP服务器配置扩展',
  autoStart: true,
  requires: [ICommandPalette],
  optional: [IMainMenu, ILayoutRestorer, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    mainMenu: IMainMenu | null,
    restorer: ILayoutRestorer | null,
    notebookTracker: INotebookTracker | null
  ) => {
    console.log('JupyterLab扩展 Jupyter MCP 已激活!');

    // 创建MCP管理器
    const mcpManager = new McpManager();

    // 创建配置面板widget跟踪器
    const configTracker = new WidgetTracker<MainAreaWidget<McpConfigPanelWidget>>({
      namespace: 'mcp-config'
    });
    
    // 创建聊天面板widget跟踪器
    const chatTracker = new WidgetTracker<MainAreaWidget<McpChatPanelWidget>>({
      namespace: 'mcp-chat'
    });

    // 如果提供了布局恢复器，则注册跟踪器
    if (restorer) {
      restorer.restore(configTracker, {
        command: CommandIDs.openConfig,
        name: () => 'mcp-config'
      });
      
      restorer.restore(chatTracker, {
        command: CommandIDs.openChatPanel,
        name: () => 'mcp-chat'
      });
    }

    // 添加命令
    app.commands.addCommand(CommandIDs.openConfig, {
      label: 'MCP服务器配置',
      execute: () => {
        // 检查是否已经打开了配置面板
        if (configTracker.currentWidget) {
          // 如果已经打开，则激活它
          app.shell.activateById(configTracker.currentWidget.id);
          return configTracker.currentWidget;
        }

        // 创建配置面板
        const content = new McpConfigPanelWidget({
          onConnect: (config: IMcpConfig) => {
            mcpManager.connect(config).then(connected => {
              if (connected) {
                console.log('已连接到MCP服务器');
              } else {
                console.error('连接到MCP服务器失败');
              }
            });
          },
          onStatusChange: (status: string) => {
            console.log('MCP状态变更:', status);
          }
        });

        // 创建主区域widget
        const widget = new MainAreaWidget({ content });
        widget.id = 'mcp-config';
        widget.title.label = 'MCP服务器配置';
        widget.title.closable = true;

        // 将widget添加到应用程序shell
        app.shell.add(widget, 'main');

        // 将widget添加到跟踪器
        configTracker.add(widget);

        return widget;
      }
    });

    app.commands.addCommand(CommandIDs.connect, {
      label: '连接到MCP服务器',
      execute: () => {
        // 如果没有配置，则打开配置面板
        if (!mcpManager.config) {
          app.commands.execute(CommandIDs.openConfig);
          return;
        }

        // 连接到MCP服务器
        mcpManager.connect(mcpManager.config).then(connected => {
          if (connected) {
            console.log('已连接到MCP服务器');
          } else {
            console.error('连接到MCP服务器失败');
          }
        });
      },
      isEnabled: () => mcpManager.status !== 'connecting'
    });

    app.commands.addCommand(CommandIDs.disconnect, {
      label: '断开MCP服务器连接',
      execute: () => {
        mcpManager.disconnect().then(() => {
          console.log('已断开MCP服务器连接');
        });
      },
      isEnabled: () => mcpManager.status === 'connected'
    });
    
    app.commands.addCommand(CommandIDs.openChatPanel, {
      label: '打开AI助手',
      execute: () => {
        // 检查是否已经打开了聊天面板
        if (chatTracker.currentWidget) {
          // 如果已经打开，则激活它
          app.shell.activateById(chatTracker.currentWidget.id);
          return chatTracker.currentWidget;
        }
        
        // 如果没有笔记本跟踪器，则无法打开聊天面板
        if (!notebookTracker) {
          console.error('未找到笔记本跟踪器，无法打开AI助手');
          return;
        }
        
        // 创建聊天面板
        const content = new McpChatPanelWidget({
          mcpManager,
          notebookTracker
        });
        
        // 创建主区域widget
        const widget = new MainAreaWidget({ content });
        widget.id = 'mcp-chat';
        widget.title.label = 'AI助手';
        widget.title.closable = true;
        
        // 将widget添加到应用程序shell的右侧面板
        app.shell.add(widget, 'right', { rank: 1000 });
        
        // 将widget添加到跟踪器
        chatTracker.add(widget);
        
        return widget;
      },
      isEnabled: () => mcpManager.status === 'connected'
    });

    // 将命令添加到命令面板
    palette.addItem({ command: CommandIDs.openConfig, category: 'MCP' });
    palette.addItem({ command: CommandIDs.connect, category: 'MCP' });
    palette.addItem({ command: CommandIDs.disconnect, category: 'MCP' });
    palette.addItem({ command: CommandIDs.openChatPanel, category: 'MCP' });

    // 如果提供了主菜单，则添加菜单项
    if (mainMenu) {
      // 直接在File菜单中添加MCP命令
      mainMenu.fileMenu.addGroup([
        { command: CommandIDs.openConfig },
        { command: CommandIDs.connect },
        { command: CommandIDs.disconnect },
        { command: CommandIDs.openChatPanel }
      ]);
      
      // 尝试添加顶级菜单
      try {
        // 创建MCP菜单
        const mcpMenu = new Menu({ commands: app.commands });
        mcpMenu.title.label = 'MCP';

        // 添加菜单项
        mcpMenu.addItem({ command: CommandIDs.openConfig });
        mcpMenu.addItem({ command: CommandIDs.connect });
        mcpMenu.addItem({ command: CommandIDs.disconnect });
        mcpMenu.addItem({ command: CommandIDs.openChatPanel });

        // 将菜单添加到主菜单
        mainMenu.addMenu(mcpMenu);
        console.log('已添加MCP顶级菜单');
      } catch (error) {
        console.error('添加MCP顶级菜单失败:', error);
      }
    }

    // 监听MCP状态变化
    mcpManager.statusChanged.connect((_, status) => {
      console.log('MCP状态变更:', status);
    });
  }
};

export default plugin;