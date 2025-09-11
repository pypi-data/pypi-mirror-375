# Generated from EsqlBaseParser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .EsqlBaseParser import EsqlBaseParser
else:
    from EsqlBaseParser import EsqlBaseParser

#
#
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. Licensed under the Elastic License
# 2.0; you may not use this file except in compliance with the Elastic License
# 2.0.
#


# This class defines a complete listener for a parse tree produced by EsqlBaseParser.
class EsqlBaseParserListener(ParseTreeListener):

    # Enter a parse tree produced by EsqlBaseParser#singleStatement.
    def enterSingleStatement(self, ctx:EsqlBaseParser.SingleStatementContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#singleStatement.
    def exitSingleStatement(self, ctx:EsqlBaseParser.SingleStatementContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#compositeQuery.
    def enterCompositeQuery(self, ctx:EsqlBaseParser.CompositeQueryContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#compositeQuery.
    def exitCompositeQuery(self, ctx:EsqlBaseParser.CompositeQueryContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#singleCommandQuery.
    def enterSingleCommandQuery(self, ctx:EsqlBaseParser.SingleCommandQueryContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#singleCommandQuery.
    def exitSingleCommandQuery(self, ctx:EsqlBaseParser.SingleCommandQueryContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#sourceCommand.
    def enterSourceCommand(self, ctx:EsqlBaseParser.SourceCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#sourceCommand.
    def exitSourceCommand(self, ctx:EsqlBaseParser.SourceCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#processingCommand.
    def enterProcessingCommand(self, ctx:EsqlBaseParser.ProcessingCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#processingCommand.
    def exitProcessingCommand(self, ctx:EsqlBaseParser.ProcessingCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#whereCommand.
    def enterWhereCommand(self, ctx:EsqlBaseParser.WhereCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#whereCommand.
    def exitWhereCommand(self, ctx:EsqlBaseParser.WhereCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#toDataType.
    def enterToDataType(self, ctx:EsqlBaseParser.ToDataTypeContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#toDataType.
    def exitToDataType(self, ctx:EsqlBaseParser.ToDataTypeContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#rowCommand.
    def enterRowCommand(self, ctx:EsqlBaseParser.RowCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#rowCommand.
    def exitRowCommand(self, ctx:EsqlBaseParser.RowCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#fields.
    def enterFields(self, ctx:EsqlBaseParser.FieldsContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#fields.
    def exitFields(self, ctx:EsqlBaseParser.FieldsContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#field.
    def enterField(self, ctx:EsqlBaseParser.FieldContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#field.
    def exitField(self, ctx:EsqlBaseParser.FieldContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#fromCommand.
    def enterFromCommand(self, ctx:EsqlBaseParser.FromCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#fromCommand.
    def exitFromCommand(self, ctx:EsqlBaseParser.FromCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#indexPattern.
    def enterIndexPattern(self, ctx:EsqlBaseParser.IndexPatternContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#indexPattern.
    def exitIndexPattern(self, ctx:EsqlBaseParser.IndexPatternContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#clusterString.
    def enterClusterString(self, ctx:EsqlBaseParser.ClusterStringContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#clusterString.
    def exitClusterString(self, ctx:EsqlBaseParser.ClusterStringContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#indexString.
    def enterIndexString(self, ctx:EsqlBaseParser.IndexStringContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#indexString.
    def exitIndexString(self, ctx:EsqlBaseParser.IndexStringContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#metadata.
    def enterMetadata(self, ctx:EsqlBaseParser.MetadataContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#metadata.
    def exitMetadata(self, ctx:EsqlBaseParser.MetadataContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#metricsCommand.
    def enterMetricsCommand(self, ctx:EsqlBaseParser.MetricsCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#metricsCommand.
    def exitMetricsCommand(self, ctx:EsqlBaseParser.MetricsCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#evalCommand.
    def enterEvalCommand(self, ctx:EsqlBaseParser.EvalCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#evalCommand.
    def exitEvalCommand(self, ctx:EsqlBaseParser.EvalCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#statsCommand.
    def enterStatsCommand(self, ctx:EsqlBaseParser.StatsCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#statsCommand.
    def exitStatsCommand(self, ctx:EsqlBaseParser.StatsCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#aggFields.
    def enterAggFields(self, ctx:EsqlBaseParser.AggFieldsContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#aggFields.
    def exitAggFields(self, ctx:EsqlBaseParser.AggFieldsContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#aggField.
    def enterAggField(self, ctx:EsqlBaseParser.AggFieldContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#aggField.
    def exitAggField(self, ctx:EsqlBaseParser.AggFieldContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#qualifiedName.
    def enterQualifiedName(self, ctx:EsqlBaseParser.QualifiedNameContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#qualifiedName.
    def exitQualifiedName(self, ctx:EsqlBaseParser.QualifiedNameContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#qualifiedNamePattern.
    def enterQualifiedNamePattern(self, ctx:EsqlBaseParser.QualifiedNamePatternContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#qualifiedNamePattern.
    def exitQualifiedNamePattern(self, ctx:EsqlBaseParser.QualifiedNamePatternContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#qualifiedNamePatterns.
    def enterQualifiedNamePatterns(self, ctx:EsqlBaseParser.QualifiedNamePatternsContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#qualifiedNamePatterns.
    def exitQualifiedNamePatterns(self, ctx:EsqlBaseParser.QualifiedNamePatternsContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#identifier.
    def enterIdentifier(self, ctx:EsqlBaseParser.IdentifierContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#identifier.
    def exitIdentifier(self, ctx:EsqlBaseParser.IdentifierContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#identifierPattern.
    def enterIdentifierPattern(self, ctx:EsqlBaseParser.IdentifierPatternContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#identifierPattern.
    def exitIdentifierPattern(self, ctx:EsqlBaseParser.IdentifierPatternContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#inputParam.
    def enterInputParam(self, ctx:EsqlBaseParser.InputParamContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#inputParam.
    def exitInputParam(self, ctx:EsqlBaseParser.InputParamContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#inputNamedOrPositionalParam.
    def enterInputNamedOrPositionalParam(self, ctx:EsqlBaseParser.InputNamedOrPositionalParamContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#inputNamedOrPositionalParam.
    def exitInputNamedOrPositionalParam(self, ctx:EsqlBaseParser.InputNamedOrPositionalParamContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#identifierOrParameter.
    def enterIdentifierOrParameter(self, ctx:EsqlBaseParser.IdentifierOrParameterContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#identifierOrParameter.
    def exitIdentifierOrParameter(self, ctx:EsqlBaseParser.IdentifierOrParameterContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#limitCommand.
    def enterLimitCommand(self, ctx:EsqlBaseParser.LimitCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#limitCommand.
    def exitLimitCommand(self, ctx:EsqlBaseParser.LimitCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#sortCommand.
    def enterSortCommand(self, ctx:EsqlBaseParser.SortCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#sortCommand.
    def exitSortCommand(self, ctx:EsqlBaseParser.SortCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#orderExpression.
    def enterOrderExpression(self, ctx:EsqlBaseParser.OrderExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#orderExpression.
    def exitOrderExpression(self, ctx:EsqlBaseParser.OrderExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#keepCommand.
    def enterKeepCommand(self, ctx:EsqlBaseParser.KeepCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#keepCommand.
    def exitKeepCommand(self, ctx:EsqlBaseParser.KeepCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#dropCommand.
    def enterDropCommand(self, ctx:EsqlBaseParser.DropCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#dropCommand.
    def exitDropCommand(self, ctx:EsqlBaseParser.DropCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#renameCommand.
    def enterRenameCommand(self, ctx:EsqlBaseParser.RenameCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#renameCommand.
    def exitRenameCommand(self, ctx:EsqlBaseParser.RenameCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#renameClause.
    def enterRenameClause(self, ctx:EsqlBaseParser.RenameClauseContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#renameClause.
    def exitRenameClause(self, ctx:EsqlBaseParser.RenameClauseContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#dissectCommand.
    def enterDissectCommand(self, ctx:EsqlBaseParser.DissectCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#dissectCommand.
    def exitDissectCommand(self, ctx:EsqlBaseParser.DissectCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#grokCommand.
    def enterGrokCommand(self, ctx:EsqlBaseParser.GrokCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#grokCommand.
    def exitGrokCommand(self, ctx:EsqlBaseParser.GrokCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#mvExpandCommand.
    def enterMvExpandCommand(self, ctx:EsqlBaseParser.MvExpandCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#mvExpandCommand.
    def exitMvExpandCommand(self, ctx:EsqlBaseParser.MvExpandCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#commandOptions.
    def enterCommandOptions(self, ctx:EsqlBaseParser.CommandOptionsContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#commandOptions.
    def exitCommandOptions(self, ctx:EsqlBaseParser.CommandOptionsContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#commandOption.
    def enterCommandOption(self, ctx:EsqlBaseParser.CommandOptionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#commandOption.
    def exitCommandOption(self, ctx:EsqlBaseParser.CommandOptionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#explainCommand.
    def enterExplainCommand(self, ctx:EsqlBaseParser.ExplainCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#explainCommand.
    def exitExplainCommand(self, ctx:EsqlBaseParser.ExplainCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#subqueryExpression.
    def enterSubqueryExpression(self, ctx:EsqlBaseParser.SubqueryExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#subqueryExpression.
    def exitSubqueryExpression(self, ctx:EsqlBaseParser.SubqueryExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#showInfo.
    def enterShowInfo(self, ctx:EsqlBaseParser.ShowInfoContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#showInfo.
    def exitShowInfo(self, ctx:EsqlBaseParser.ShowInfoContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#enrichCommand.
    def enterEnrichCommand(self, ctx:EsqlBaseParser.EnrichCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#enrichCommand.
    def exitEnrichCommand(self, ctx:EsqlBaseParser.EnrichCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#enrichWithClause.
    def enterEnrichWithClause(self, ctx:EsqlBaseParser.EnrichWithClauseContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#enrichWithClause.
    def exitEnrichWithClause(self, ctx:EsqlBaseParser.EnrichWithClauseContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#lookupCommand.
    def enterLookupCommand(self, ctx:EsqlBaseParser.LookupCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#lookupCommand.
    def exitLookupCommand(self, ctx:EsqlBaseParser.LookupCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#inlinestatsCommand.
    def enterInlinestatsCommand(self, ctx:EsqlBaseParser.InlinestatsCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#inlinestatsCommand.
    def exitInlinestatsCommand(self, ctx:EsqlBaseParser.InlinestatsCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#joinCommand.
    def enterJoinCommand(self, ctx:EsqlBaseParser.JoinCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#joinCommand.
    def exitJoinCommand(self, ctx:EsqlBaseParser.JoinCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#joinTarget.
    def enterJoinTarget(self, ctx:EsqlBaseParser.JoinTargetContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#joinTarget.
    def exitJoinTarget(self, ctx:EsqlBaseParser.JoinTargetContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#joinCondition.
    def enterJoinCondition(self, ctx:EsqlBaseParser.JoinConditionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#joinCondition.
    def exitJoinCondition(self, ctx:EsqlBaseParser.JoinConditionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#joinPredicate.
    def enterJoinPredicate(self, ctx:EsqlBaseParser.JoinPredicateContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#joinPredicate.
    def exitJoinPredicate(self, ctx:EsqlBaseParser.JoinPredicateContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#insistCommand.
    def enterInsistCommand(self, ctx:EsqlBaseParser.InsistCommandContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#insistCommand.
    def exitInsistCommand(self, ctx:EsqlBaseParser.InsistCommandContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#matchExpression.
    def enterMatchExpression(self, ctx:EsqlBaseParser.MatchExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#matchExpression.
    def exitMatchExpression(self, ctx:EsqlBaseParser.MatchExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#logicalNot.
    def enterLogicalNot(self, ctx:EsqlBaseParser.LogicalNotContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#logicalNot.
    def exitLogicalNot(self, ctx:EsqlBaseParser.LogicalNotContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#booleanDefault.
    def enterBooleanDefault(self, ctx:EsqlBaseParser.BooleanDefaultContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#booleanDefault.
    def exitBooleanDefault(self, ctx:EsqlBaseParser.BooleanDefaultContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#isNull.
    def enterIsNull(self, ctx:EsqlBaseParser.IsNullContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#isNull.
    def exitIsNull(self, ctx:EsqlBaseParser.IsNullContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#regexExpression.
    def enterRegexExpression(self, ctx:EsqlBaseParser.RegexExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#regexExpression.
    def exitRegexExpression(self, ctx:EsqlBaseParser.RegexExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#logicalIn.
    def enterLogicalIn(self, ctx:EsqlBaseParser.LogicalInContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#logicalIn.
    def exitLogicalIn(self, ctx:EsqlBaseParser.LogicalInContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#logicalBinary.
    def enterLogicalBinary(self, ctx:EsqlBaseParser.LogicalBinaryContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#logicalBinary.
    def exitLogicalBinary(self, ctx:EsqlBaseParser.LogicalBinaryContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#regexBooleanExpression.
    def enterRegexBooleanExpression(self, ctx:EsqlBaseParser.RegexBooleanExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#regexBooleanExpression.
    def exitRegexBooleanExpression(self, ctx:EsqlBaseParser.RegexBooleanExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#matchBooleanExpression.
    def enterMatchBooleanExpression(self, ctx:EsqlBaseParser.MatchBooleanExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#matchBooleanExpression.
    def exitMatchBooleanExpression(self, ctx:EsqlBaseParser.MatchBooleanExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#valueExpressionDefault.
    def enterValueExpressionDefault(self, ctx:EsqlBaseParser.ValueExpressionDefaultContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#valueExpressionDefault.
    def exitValueExpressionDefault(self, ctx:EsqlBaseParser.ValueExpressionDefaultContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#comparison.
    def enterComparison(self, ctx:EsqlBaseParser.ComparisonContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#comparison.
    def exitComparison(self, ctx:EsqlBaseParser.ComparisonContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#operatorExpressionDefault.
    def enterOperatorExpressionDefault(self, ctx:EsqlBaseParser.OperatorExpressionDefaultContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#operatorExpressionDefault.
    def exitOperatorExpressionDefault(self, ctx:EsqlBaseParser.OperatorExpressionDefaultContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#arithmeticBinary.
    def enterArithmeticBinary(self, ctx:EsqlBaseParser.ArithmeticBinaryContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#arithmeticBinary.
    def exitArithmeticBinary(self, ctx:EsqlBaseParser.ArithmeticBinaryContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#arithmeticUnary.
    def enterArithmeticUnary(self, ctx:EsqlBaseParser.ArithmeticUnaryContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#arithmeticUnary.
    def exitArithmeticUnary(self, ctx:EsqlBaseParser.ArithmeticUnaryContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#dereference.
    def enterDereference(self, ctx:EsqlBaseParser.DereferenceContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#dereference.
    def exitDereference(self, ctx:EsqlBaseParser.DereferenceContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#inlineCast.
    def enterInlineCast(self, ctx:EsqlBaseParser.InlineCastContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#inlineCast.
    def exitInlineCast(self, ctx:EsqlBaseParser.InlineCastContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#constantDefault.
    def enterConstantDefault(self, ctx:EsqlBaseParser.ConstantDefaultContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#constantDefault.
    def exitConstantDefault(self, ctx:EsqlBaseParser.ConstantDefaultContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#parenthesizedExpression.
    def enterParenthesizedExpression(self, ctx:EsqlBaseParser.ParenthesizedExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#parenthesizedExpression.
    def exitParenthesizedExpression(self, ctx:EsqlBaseParser.ParenthesizedExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#function.
    def enterFunction(self, ctx:EsqlBaseParser.FunctionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#function.
    def exitFunction(self, ctx:EsqlBaseParser.FunctionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#functionExpression.
    def enterFunctionExpression(self, ctx:EsqlBaseParser.FunctionExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#functionExpression.
    def exitFunctionExpression(self, ctx:EsqlBaseParser.FunctionExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#functionName.
    def enterFunctionName(self, ctx:EsqlBaseParser.FunctionNameContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#functionName.
    def exitFunctionName(self, ctx:EsqlBaseParser.FunctionNameContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#mapExpression.
    def enterMapExpression(self, ctx:EsqlBaseParser.MapExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#mapExpression.
    def exitMapExpression(self, ctx:EsqlBaseParser.MapExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#entryExpression.
    def enterEntryExpression(self, ctx:EsqlBaseParser.EntryExpressionContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#entryExpression.
    def exitEntryExpression(self, ctx:EsqlBaseParser.EntryExpressionContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#nullLiteral.
    def enterNullLiteral(self, ctx:EsqlBaseParser.NullLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#nullLiteral.
    def exitNullLiteral(self, ctx:EsqlBaseParser.NullLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#qualifiedIntegerLiteral.
    def enterQualifiedIntegerLiteral(self, ctx:EsqlBaseParser.QualifiedIntegerLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#qualifiedIntegerLiteral.
    def exitQualifiedIntegerLiteral(self, ctx:EsqlBaseParser.QualifiedIntegerLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#decimalLiteral.
    def enterDecimalLiteral(self, ctx:EsqlBaseParser.DecimalLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#decimalLiteral.
    def exitDecimalLiteral(self, ctx:EsqlBaseParser.DecimalLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#integerLiteral.
    def enterIntegerLiteral(self, ctx:EsqlBaseParser.IntegerLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#integerLiteral.
    def exitIntegerLiteral(self, ctx:EsqlBaseParser.IntegerLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#booleanLiteral.
    def enterBooleanLiteral(self, ctx:EsqlBaseParser.BooleanLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#booleanLiteral.
    def exitBooleanLiteral(self, ctx:EsqlBaseParser.BooleanLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#inputParameter.
    def enterInputParameter(self, ctx:EsqlBaseParser.InputParameterContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#inputParameter.
    def exitInputParameter(self, ctx:EsqlBaseParser.InputParameterContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#stringLiteral.
    def enterStringLiteral(self, ctx:EsqlBaseParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#stringLiteral.
    def exitStringLiteral(self, ctx:EsqlBaseParser.StringLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#numericArrayLiteral.
    def enterNumericArrayLiteral(self, ctx:EsqlBaseParser.NumericArrayLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#numericArrayLiteral.
    def exitNumericArrayLiteral(self, ctx:EsqlBaseParser.NumericArrayLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#booleanArrayLiteral.
    def enterBooleanArrayLiteral(self, ctx:EsqlBaseParser.BooleanArrayLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#booleanArrayLiteral.
    def exitBooleanArrayLiteral(self, ctx:EsqlBaseParser.BooleanArrayLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#stringArrayLiteral.
    def enterStringArrayLiteral(self, ctx:EsqlBaseParser.StringArrayLiteralContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#stringArrayLiteral.
    def exitStringArrayLiteral(self, ctx:EsqlBaseParser.StringArrayLiteralContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#booleanValue.
    def enterBooleanValue(self, ctx:EsqlBaseParser.BooleanValueContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#booleanValue.
    def exitBooleanValue(self, ctx:EsqlBaseParser.BooleanValueContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#numericValue.
    def enterNumericValue(self, ctx:EsqlBaseParser.NumericValueContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#numericValue.
    def exitNumericValue(self, ctx:EsqlBaseParser.NumericValueContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#decimalValue.
    def enterDecimalValue(self, ctx:EsqlBaseParser.DecimalValueContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#decimalValue.
    def exitDecimalValue(self, ctx:EsqlBaseParser.DecimalValueContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#integerValue.
    def enterIntegerValue(self, ctx:EsqlBaseParser.IntegerValueContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#integerValue.
    def exitIntegerValue(self, ctx:EsqlBaseParser.IntegerValueContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#string.
    def enterString(self, ctx:EsqlBaseParser.StringContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#string.
    def exitString(self, ctx:EsqlBaseParser.StringContext):
        pass


    # Enter a parse tree produced by EsqlBaseParser#comparisonOperator.
    def enterComparisonOperator(self, ctx:EsqlBaseParser.ComparisonOperatorContext):
        pass

    # Exit a parse tree produced by EsqlBaseParser#comparisonOperator.
    def exitComparisonOperator(self, ctx:EsqlBaseParser.ComparisonOperatorContext):
        pass



del EsqlBaseParser